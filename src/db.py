import asyncio
import boto3
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from src.functions import get_logger
from src.config import base_config
from botocore.exceptions import ClientError
import io

logger = get_logger(__name__)

class DBClient:
    def __init__(self) -> None:
        self._database = "shaulink.db"
        self._url = f"sqlite+aiosqlite:///{self._database}"

    async def get_async_engine(self):
        try:
            engine = create_async_engine(
                self._url,
                echo=False,
            )
            yield engine
        finally:
            await engine.dispose()

    async def get_async_session(self, async_engine):
        async_session = async_sessionmaker(async_engine, expire_on_commit=False)
        return async_session

class RedisClient:
    def __init__(self) -> None:
        self._host = "redis"
        self._port = 6379
        self._db = 0
    
    async def get_connection(self):
        try:
            r = redis.from_url(
                url=f"redis://{self._host}:{self._port}",
                db=self._db,
                decode_responses=True
            )
            yield r
        finally:
            await r.close()

class ObjectStorageClient:
    def __init__(self) -> None:
        self.image_bucket_name = "image-dtheva"
        self.video_bucket_name = "video-um1vqw"
        self.init()
        
    def init(self):
        s3_client = self.get_s3_client()
        buckets = self.list_buckets(s3_client)
        if self.image_bucket_name not in buckets:
            assert self.create_bucket(s3_client, bucket_name=self.image_bucket_name) is True, "failed to create image bucket."
        if self.video_bucket_name not in buckets:
            assert self.create_bucket(s3_client, bucket_name=self.video_bucket_name) is True, "failed to create video bucket."

    def get_s3_client(self, bucket_name: str = None):
        if bucket_name is not None:
            return boto3.client(
                's3',
                endpoint_url=f"{base_config.object_storage.hostname}/{bucket_name}",
                aws_access_key_id=base_config.object_storage.access_key,
                aws_secret_access_key=base_config.object_storage.secret_key,
            )
        else:
            return boto3.client(
                's3',
                endpoint_url=base_config.object_storage.hostname,
                aws_access_key_id=base_config.object_storage.access_key,
                aws_secret_access_key=base_config.object_storage.secret_key,
            )

    def list_buckets(self, s3_client):
        response = s3_client.list_buckets()
        return [bucket["Name"] for bucket in response["Buckets"]]
    
    def create_bucket(self, s3_client, bucket_name):
        # Create bucket
        try:
            s3_client.create_bucket(Bucket=bucket_name)
        except ClientError as e:
            logger.error(e)
            return False
        return True
    
    def upload_file_object(
        self,
        s3_client,
        file: bytes,
        object_name: str,
        bucket_name: str,
        metadata: dict
    ):
        # Upload the file
        try:
            response = s3_client.upload_fileobj(
                io.BytesIO(file),
                bucket_name,
                object_name,
                ExtraArgs={'Metadata': metadata}
            )
        except ClientError as e:
            logger.error(e)
            return False
        return True
    
    def get_head_object(
        self,
        s3_client,
        bucket_name: str,
        object_name: str
    ):
        response = s3_client.head_object(
            Bucket=bucket_name,
            Key=object_name,
        )
        return response
    
    def download_file_object(
        self,
        s3_client,
        bucket_name: str,
        object_name: str
    ):
        # Upload the file
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
            metadata = response["Metadata"]
            file_content = response['Body'].read()
            return file_content, metadata
        
        except ClientError as e:
            logger.error(e)
            return False
        return True
    
if __name__ == "__main__":
    ob = ObjectStorageClient()

    