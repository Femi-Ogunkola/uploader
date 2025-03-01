import os
import grpc
from concurrent import futures
import os
from stubs import media_pb2
from stubs import media_pb2_grpc
from s3client import S3Client

from dotenv import load_dotenv

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
                    video_file_path = f"{self.upload_directory}/{video_id}.mp4"
                    with open(video_file_path, 'wb') as video_file:
                        video_file.write(video_data)
                    yield media_pb2.UploadVideoResponse(
                        status="success",
                        message="Video uploaded successfully",
                        progress=100,
                        )
            
            self.s3Client.upload_video_file(filename=f"{video_file_path}", shouldForceVideo=False)

        except Exception as e:
            return media_pb2.UploadVideoResponse(
                status="failure",
                message=f"An error occurred during upload: {str(e)}",
                progress=0,
            )
    
    def _generate_video_id(self):
        # You could implement your own video ID generation logic here
        return str(os.urandom(8).hex())

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
