from config import Config
import boto3
from PIL import Image
import io

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

    def upload_image(self, objectKey: str, image: Image):
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        self.s3.upload_fileobj(buffer, self.bucket, objectKey)
        return objectKey
    def download_image(self, objectKey: str):
        response = self.s3.get_object(Bucket=self.bucket, Key=objectKey)
        image_bytes = response['Body'].read()
        image = Image.open(io.BytesIO(image_bytes))
        return image