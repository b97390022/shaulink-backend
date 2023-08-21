from fastapi import APIRouter, Depends, HTTPException, Header, status
from src.db import RedisClient, DBClient
from sqlalchemy.ext.asyncio import AsyncEngine
import requests
from bs4 import BeautifulSoup
import src.functions as functions
import src.models as models
import src.crud as crud
from src.config import base_config
from src.functions import get_logger

logger = get_logger(__name__)

router = APIRouter()
redis_client = RedisClient()
db_client = DBClient()

async def get_og_info(long_url: str):
    title = url = image = description = ""
    try:
        r = requests.get(long_url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            og_title = soup.find("meta", property="og:title")
            og_url = soup.find("meta", property="og:url")
            og_image = soup.find("meta", property="og:image")
            og_description = soup.find("meta", property="og:description")

            title = og_title["content"] if og_title else ""
            url = og_url["content"] if og_url else ""
            image = og_image["content"] if og_image else ""
            description = og_description["content"] if og_description else ""
        return {
            "title": title,
            "url": url,
            "image": image,
            "description": description
        }
    except:
        return {
            "title": title,
            "url": url,
            "image": image,
            "description": description
        }

@router.get("/{hash}")
async def get_data(
    hash: str,
    async_engine: AsyncEngine = Depends(db_client.get_async_engine)
    
):
    detail_message = "Data not found!"
    objects = await crud.get_objects(
        hash,
        await db_client.get_async_session(async_engine)
    )
    try:
        if objects:
            return {
                "type": objects["type"],
                "data": objects["data"],
                "password": objects["password"],
                "og_title": objects["og_title"],
                "og_url": objects["og_url"],
                "og_image": objects["og_image"],
                "og_description": objects["og_description"],
                "create_time": objects["create_time"],
                "expired": objects["expired"],
            }
        else:
            raise HTTPException(status_code=404, detail=detail_message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='There was an error when getting hash.'
        )