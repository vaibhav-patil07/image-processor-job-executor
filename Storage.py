from config import Config
import boto3
from PIL import Image
import io
import cv2
import numpy as np
class Storage:
    def __init__(self, config: Config):
        self.config = config
        self.bucket = config.STORAGE_BUCKET
        self.s3 = boto3.client(
            's3',
            endpoint_url=config.STORAGE_END_POINT,
            region_name=config.STORAGE_REGION,
            aws_access_key_id=config.ACCESS_KEY,
            aws_secret_access_key=config.SECRET_KEY
        )

    def upload_image(self, objectKey: str, image: np.ndarray):
        buffer = io.BytesIO(image)
        buffer.seek(0)
        self.s3.upload_fileobj(buffer, self.bucket, objectKey)
        return objectKey

    def download_image(self, objectKey: str):
        response = self.s3.get_object(Bucket=self.bucket, Key=objectKey)
        image_bytes = response['Body'].read()
        img = cv2.imdecode(np.asarray(bytearray(image_bytes)), cv2.IMREAD_COLOR)
        return img