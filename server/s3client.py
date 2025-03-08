import logging
from typing import Optional
from urllib.parse import urlparse

import boto3  # type: ignore
from botocore.exceptions import NoCredentialsError


class UnplannedVideoURLException(BaseException):
    pass

class S3Client:

    def __init__(self, accessKey: str, accessSecretKey: str, bucketName: str, region: str) -> None:
        self.accessKey = accessKey
        self.accessSecretKey = accessSecretKey
        self.bucketName = bucketName
        self.region = region
        self.s3client =  boto3.client('s3', aws_access_key_id=self.accessKey,aws_secret_access_key=self.accessSecretKey)

    async def download_s3_video_file(self, s3Url: str, filename: str) -> str:
        url = urlparse(s3Url)
        objectName = url.path.replace("/",'',1)
        if "/" in objectName:
            objectName = objectName.split('/')[1]
        if objectName != "" :
            self.s3client.download_file(self.bucketName, objectName, f'{filename}.mp4')
            return f'{filename}.mp4'
        raise UnplannedVideoURLException()

    def upload_video_file(self, filename: str, shouldForceVideo: Optional[bool] = True) -> str:
        doesFileExist = self.does_file_exists(filename=filename)
        if doesFileExist and not shouldForceVideo:
            url = self.generate_url(filename=filename)
            logging.info("Url retrieved")
            return url
        try:
            print(filename, self.bucketName)
            self.s3client.upload_file(filename, self.bucketName, filename ,ExtraArgs={'ContentType': "video/mp4"})
            url = self.generate_url(filename=filename)
            logging.info("Upload Successful")
            return url
        except FileNotFoundError as exception:
            raise exception
        except NoCredentialsError as exception:
            raise exception

    def does_file_exists(self, filename: str) -> bool:
        try:
            self.s3client.head_object(Bucket=self.bucketName, Key=filename)
            return True
        except: #pylint: disable=bare-except
            return False

    def generate_url(self, filename: str) -> str:
        return f"https://{self.bucketName}.s3.amazonaws.com/{filename}"
