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
        video_id = 'upload_test'
        video_data = b''
        try:
            # Process the stream
            for chunk in request_iterator:
                #  Process video chunk
                print(f"Received chunk {chunk.chunk_index} (size: {len(chunk.data)} bytes, last_chunk {chunk.is_last_chunk})")
                if chunk.chunk_index == 0:
                    video_id = str(chunk.data, 'utf-8')
                else:
                    video_data += chunk.data  # Append video chunk to video_data
                    if chunk.is_last_chunk:
                        print(f"Final chunk received (chunk {chunk.chunk_index}), saving video to disk...")
                        video_file_path = f"{self.upload_directory}/{video_id}.mp4"
                        # os.makedirs(os.path.dirname(video_file_path), exist_ok=True)

                        # Save the video data to a file once the last chunk is received
                        with open(video_file_path, 'wb') as video_file:
                            video_file.write(video_data)

                        print(f"Video saved to {video_file_path}")
            
            # Close the file after all chunks are written
            if video_file:
                video_file.close()
            
            self.s3Client.upload_video_file(filename=f"{video_file_path}", shouldForceVideo=False)
            
            # Respond to the client with the video ID and status
            return media_pb2.UploadVideoResponse(
                status="success",
                video_id=video_id,
                message="Video uploaded successfully"
            )
        except Exception as e:
            # Handle errors in the video upload
            if video_file:
                video_file.close()
            return media_pb2.UploadVideoResponse(
                status="failure",
                video_id="",
                message=f"An error occurred during upload: {str(e)}"
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
