import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile, Response
from fastapi.responses import FileResponse
from src.db import RedisClient, DBClient, ObjectStorageClient
import src.crud as crud
from sqlalchemy.ext.asyncio import AsyncEngine
from redis.asyncio.client import Redis
import src.functions as functions
import src.models as models
from src.config import base_config
from src.functions import get_logger
from typing import Annotated
from src.routers.base_router import get_og_info

logger = get_logger(__name__)

router = APIRouter(prefix="/image")
redis_client = RedisClient()
db_client = DBClient()
object_storage_client = ObjectStorageClient()

@router.post("")
async def process_image(
    files: Annotated[UploadFile, File()],
    formId: Annotated[str, Form()],
    media_type: Annotated[str, Form()],
    password: Annotated[str, Form()] = "",
    async_engine: AsyncEngine = Depends(db_client.get_async_engine)
):
    try:
        object_name = functions.generate_base64_random_hash()

        s3_client = object_storage_client.get_s3_client(object_storage_client.image_bucket_name)
        upload_status = object_storage_client.upload_file_object(
            s3_client,
            await files.read(),
            object_name,
            object_storage_client.image_bucket_name,
            metadata={
                "x-amz-media-type": media_type
            }
        )
        assert upload_status is True, "upload to s3 storage failed."
        # async with aiofiles.open(file_path, 'wb') as file:
        #     content = await files.read()  # async read
        #     await file.write(content)  # async write

        id_ = await crud.insert_objects({
            "id": formId,
            "type": 2,
            "password": password,
            "og_title": "",
            "og_url": "",
            "og_image": "",
            "og_description": "",
            "object_name": object_name,
            "media_type": media_type
        }, await db_client.get_async_session(async_engine))


    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='There was an error when uploading file.'
        ) 
    return {
        "data":{
            "shortUrl": f"{'https' if base_config.domain != 'localhost' else 'http'}://{base_config.domain}/{id_}",
        }
    }

@router.get("/{object_name}")
async def get_image(
    object_name: str
):
    try:
        s3_client = object_storage_client.get_s3_client(object_storage_client.image_bucket_name)
        image, metadata = object_storage_client.download_file_object(s3_client, object_storage_client.image_bucket_name, object_name)
        return Response(
            content=image,
            media_type=metadata["x-amz-media-type"]
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='There was an error when downloading file.'
        )