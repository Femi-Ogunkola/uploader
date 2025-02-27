import grpc
import os
import media_pb2
import media_pb2_grpc
import argparse

CHUNK_SIZE = 1024 * 1024  # 1MB per chunk, you can adjust this as needed

class VideoUploader:
    def __init__(self, video_file_path):
        self.video_file_path = video_file_path
        self.video_metadata = self._get_video_metadata()

    def _get_video_metadata(self):
        # Get basic metadata about the video file
        video_metadata = media_pb2.VideoMetadata()
        video_metadata.file_name = os.path.basename(self.video_file_path)
        video_metadata.content_type = "video/mp4"  # Set the content type to match the video format
        video_metadata.file_size = os.path.getsize(self.video_file_path)
        return video_metadata

    def _read_video_in_chunks(self):
        # Read the video file in chunks
        with open(self.video_file_path, 'rb') as video_file:
            while True:
                chunk_data = video_file.read(CHUNK_SIZE)
                if not chunk_data:
                    break
                yield chunk_data

    def upload_video(self):
        # Create a gRPC channel and stub
        channel = grpc.insecure_channel('localhost:50051')
        stub = media_pb2_grpc.VideoUploadServiceStub(channel)

        # Add debugging to check metadata before sending
        print(f"Video Metadata: {self.video_metadata}")

        # Send metadata first, then start streaming video chunks
        try:
            # Create the generator to send chunks
            def video_chunk_generator():
                # Send the metadata first as the first chunk in the stream
                yield media_pb2.VideoChunk(
                    data=b'',  # Empty data to signal metadata (does not need to be actual chunk)
                    chunk_index=-1,  # Not an actual video chunk
                    is_last_chunk=False  # This is not the last chunk
                )

                # Now send actual video chunks
                chunk_index = 0
                for chunk_data in self._read_video_in_chunks():
                    is_last_chunk = False
                    if chunk_index * CHUNK_SIZE + len(chunk_data) == self.video_metadata.file_size:
                        is_last_chunk = True  # Mark the last chunk

                    # Send actual video chunk
                    video_chunk = media_pb2.VideoChunk(
                        data=chunk_data,
                        chunk_index=chunk_index,
                        is_last_chunk=is_last_chunk
                    )
                    yield video_chunk
                    chunk_index += 1

            # Send the metadata with the upload request
            upload_request = media_pb2.UploadVideoRequest(metadata=self.video_metadata)
            response = stub.UploadVideo(video_chunk_generator())

            print(f"Upload status: {response.status}")
            if response.status == "success":
                print(f"Video ID: {response.video_id}")
            else:
                print(f"Error message: {response.message}")

        except grpc.RpcError as e:
            print(f"gRPC Error: {e}")
            print(f"Details: {e.details()}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Upload a video file to the server.")
    parser.add_argument('video_file_path', type=str, help="Path to the video file to upload")

    # Parse the arguments
    args = parser.parse_args()

    # Make sure the file exists
    if not os.path.exists(args.video_file_path):
        print(f"Error: The file at {args.video_file_path} does not exist.")
    else:
        # Create a VideoUploader instance and start uploading the video
        uploader = VideoUploader(args.video_file_path)
        uploader.upload_video()