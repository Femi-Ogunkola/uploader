import os
import grpc
import subprocess
from concurrent import futures
import ffmpeg
import time


from stubs import media_pb2
from stubs import media_pb2_grpc
from s3client import S3Client

from dotenv import load_dotenv

CHUNK_SIZE = 1024 * 1024
INIT_SEGMENT_SIZE = 1024

class VideoUploadService(media_pb2_grpc.VideoUploadServiceServicer):
    def __init__(self, s3Client: S3Client):
        self.upload_directory = "uploaded_videos"  # Directory to store video files
        self.s3Client = s3Client
    
    def UploadVideo(self, request_iterator, context):
        # Prepare the video upload (we'll save it with the metadata)
        default_video_id = 'upload_test'
        video_data = b''
        total_chunks = 0
        try:
            # Process the stream
            for chunk in request_iterator:
                #  Process video chunk
                print(f"Received chunk {chunk.chunk_index} (size: {len(chunk.data)} bytes, last_chunk {chunk.is_last_chunk})")
                if chunk.chunk_index == 0:
                    video_meta = str(chunk.data, 'utf-8').split('-')
                    video_id, total_chunks = video_meta
                    total_chunks = int(total_chunks)
                else:
                    progress = int((chunk.chunk_index/total_chunks) * 100)
                    video_data += chunk.data  # Append video chunk to video_data
                    status=media_pb2.Status(
                        status='GOOD',
                        message='Uploading',
                        progress=progress
                    )
                    yield media_pb2.UploadVideoResponse(
                        status=status
                    )

                if chunk.is_last_chunk:
                    print(f"Final chunk received (chunk {chunk.chunk_index}), saving video to disk...")
                    video_file_path = f"{video_id}.mp4"
                    with open(video_file_path, 'wb') as video_file:
                        video_file.write(video_data)
                    status=media_pb2.Status(
                        status='success',
                        message='Uploading',
                        progress=100
                    )
                    yield media_pb2.UploadVideoResponse(
                        status=status
                    )
                    print("Uploading to s3")
                    self.s3Client.upload_video_file(filename=f"{video_id}.mp4", shouldForceVideo=False)
                    print("done Uploading to s3")

        except Exception as e:
            status=media_pb2.Status(
                status='failed',
                message=str(e),
                progress=0
            )
            yield media_pb2.UploadVideoResponse(
                status=status,
            )
    
    def _generate_video_id(self):
        # You could implement your own video ID generation logic here
        return str(os.urandom(8).hex())

    def convert_to_fragmented_h264(self, input_video_path, output_video_path):
        """Converts the video to fragmented H.264 format using FFmpeg."""
        if os.path.exists(output_video_path):
            print("✅ Fragmented H.264 video already exists. Skipping conversion.")
            return output_video_path  # Already converted

        # Add before the conversion to check input streams
        probe = ffmpeg.probe(input_video_path)
        audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
        print(f"Found {len(audio_streams)} audio streams in input file")
        print("⏳ Converting video to fragmented H.264...")
        try:
                # The key flags here are: -movflags frag_keyframe+empty_moov+default_base_moof
            # These ensure the MP4 is fragmented and MSE-compatible
            temp_output = output_video_path + ".temp.mp4"
            
            (
                ffmpeg
                .input(input_video_path)
                .output(
                    temp_output, 
                    vcodec="libx264",
                    acodec="aac",
                    movflags="faststart",
                    preset="fast",
                    # Additional parameters for better web compatibility
                    level="3.0",
                    pix_fmt="yuv420p",
                    # Audio parameters
                    ar="44100",  # Sample rate
                    ab="128k"    # Bitrate
                )
                .run(overwrite_output=True, quiet=False)
            )
            # Then, fragment the MP4 for MSE
            (
                ffmpeg
                .input(temp_output)
                .output(
                    output_video_path,
                    c="copy",  # Just copy the streams without re-encoding
                    movflags="frag_keyframe+empty_moov+default_base_moof+separate_moof",
                    # Use smaller fragments for better streaming
                    frag_duration="500",  # 500ms fragments
                )
                .run(overwrite_output=True, quiet=False)
            )
        
            # Clean up the temporary file
            try:
                os.remove(temp_output)
            except:
                print("⚠️ Failed to remove temporary file")
                print("✅ Conversion completed.")
            return output_video_path
        except ffmpeg.Error as e:
            print("❌ FFmpeg error:", e.stderr)
            raise RuntimeError("FFmpeg conversion failed")

    def StreamVideo(self, request, context):
        """Streams the fragmented H.264 video in chunks over gRPC."""
        video_path = self.convert_to_fragmented_h264()  # Ensure it's in fragmented H.264 format

        try:
            with open(video_path, "rb") as video_file:
                # First, extract the init segment (moov box) from the beginning of the file
                # The init segment contains codec information needed by MSE
                init_data = video_file.read(INIT_SEGMENT_SIZE)  # Usually around 1KB, but can vary
                
                yield media_pb2.VideoChunk(
                    data=init_data,
                    chunk_index=0,
                    chunk_type="init"  # Add this field to your protobuf definition
                )
                
                chunk_index = 1
                while True:
                    chunk = video_file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    yield media_pb2.VideoChunk(
                        data=chunk, 
                        chunk_index=chunk_index,
                        chunk_type="media"  # Regular media segment
                    )
                    chunk_index += 1
                    time.sleep(0.1)  # Simulate network delay
        except Exception as e:
            print(f"❌ Error streaming video: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to stream video")

def serve():
    load_dotenv('.env')
    ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
    SECRET_KEY = os.getenv("S3_ACCESS_SECRET_KEY")
    BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    REGION = os.getenv("S3_REGION")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    s3Client = S3Client(accessKey=ACCESS_KEY, accessSecretKey=SECRET_KEY, bucketName=BUCKET_NAME, region=REGION)
    media_pb2_grpc.add_VideoUploadServiceServicer_to_server(VideoUploadService(s3Client=s3Client), server)
    server.add_insecure_port('[::]:50051')
    print("Server started on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
