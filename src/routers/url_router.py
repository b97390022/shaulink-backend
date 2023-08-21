from fastapi import APIRouter, Depends, HTTPException, Header
from src.db import RedisClient, DBClient
from sqlalchemy.ext.asyncio import AsyncEngine
import src.functions as functions
import src.models as models
import src.crud as crud
from src.config import base_config
from src.functions import get_logger
from src.routers.base_router import get_og_info

logger = get_logger(__name__)

router = APIRouter()
redis_client = RedisClient()
db_client = DBClient()

@router.post("/shorten")
async def shorten_url(
    url_item: models.UrlItem,
    async_engine: AsyncEngine = Depends(db_client.get_async_engine)
):
    long_url = str(url_item.url)
    og_info = await get_og_info(long_url)

    id_ = await crud.insert_objects({
        "type": 1,
        "password": "",
        "og_title": og_info.get("title", ""),
        "og_url": og_info.get("url", ""),
        "og_image": og_info.get("image", ""),
        "og_description": og_info.get("description", ""),
        "long_url": long_url,
    }, await db_client.get_async_session(async_engine))
   
    return {
        "data":{
            "shortUrl": f"{'https' if base_config.domain != 'localhost' else 'http'}://{base_config.domain}/{id_}",
        }
    }