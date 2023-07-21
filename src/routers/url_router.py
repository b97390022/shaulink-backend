from fastapi import APIRouter, Depends, HTTPException
from src.db import RedisClient
from redis.asyncio.client import Redis
import src.functions as functions
import src.models as models
from src.config import base_config

router = APIRouter()
redis_client = RedisClient()

@router.get('/{url}')
async def get_long_url(
    url: str,
    redis_connection: Redis = Depends(redis_client.get_connection)
):
    if await redis_connection.exists(url):
        long_url = await redis_connection.get(url)
        return {
            "long_url": long_url,
        }
    else:
        raise HTTPException(status_code=404, detail="Short URL not found!")
    
@router.post("/shorten/")
async def shorten_url(
    url_item: models.UrlItem,
    redis_connection: Redis = Depends(redis_client.get_connection)
):
    long_url = str(url_item.url)
    
    if await redis_connection.exists(long_url):
        return await redis_connection.get(long_url)

    random_hash = functions.generate_base64_random_hash()

    while await redis_connection.exists(random_hash):
        random_hash = functions.generate_base64_random_hash()

    await redis_connection.set(random_hash, long_url, ex=base_config.url_ttl)
    return f"https://{base_config.domain}/{random_hash}"