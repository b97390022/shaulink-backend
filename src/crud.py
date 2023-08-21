import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import src.functions as functions
from src.db import DBClient
import src.schemas as schemas
from cachetools import TTLCache

id_cache = TTLCache(maxsize=128, ttl=10 * 60)

db_client = DBClient()

async def insert_objects(
    object_: dict,
    async_session: async_sessionmaker[AsyncSession]
):
    async with async_session() as session:
        async with session.begin():
            stmt = select(schemas.Item).where(schemas.Item.id==object_.get("id"))
            item = (await session.scalars(stmt)).one_or_none()
            id_ = object_.get("id") or functions.generate_base64_random_hash()
            if id_cache.get(id_) is None:
                id_cache[id_] = True
                item = schemas.Item(
                    id=id_,
                    type=object_["type"],
                    password=object_["password"],
                    og_title=object_["og_title"],
                    og_url=object_["og_url"],
                    og_image=object_["og_image"],
                    og_description=object_["og_description"],
                )
                match object_["type"]:
                    case 1:
                        item.url = [schemas.URL(
                            item_id=id_,
                            data=object_["long_url"]
                        )]
                    case 2:
                        item.image = [schemas.Image(
                            item_id=id_,
                            data=object_["object_name"],
                            media_type=object_["media_type"]
                        )]
                    case 3:
                        item.video = [schemas.Video(
                            item_id=id_,
                            data=object_["object_name"],
                            media_type=object_["media_type"]
                        )]
            else:
                match object_["type"]:
                    case 1:
                        item = schemas.URL(
                            item_id=id_,
                            data=object_["long_url"]
                        )
                    case 2:
                        item = schemas.Image(
                            item_id=id_,
                            data=object_["object_name"],
                            media_type=object_["media_type"]
                        )
                    case 3:
                        item = schemas.Video(
                            item_id=id_,
                            data=object_["object_name"],
                            media_type=object_["media_type"]
                        )
            
            session.add_all(
                [
                    item,
                ]
            )
    return id_

async def get_objects(
    id: str,
    async_session: async_sessionmaker[AsyncSession]
):
    
    object_ = {}

    async with async_session() as session:
        async with session.begin():
            stmt = select(schemas.Item.type).where(schemas.Item.id==id)
            type_ = (await session.scalars(stmt)).one_or_none()
            if type_ is None:
                return object_
            stmt = select(schemas.Item).options(selectinload(
                schemas.Item.url if type_ == 1
                else schemas.Item.image if type_ == 2
                else schemas.Item.video if type_ == 3
                else None
            )).where(schemas.Item.id==id)
            result = await session.execute(stmt)
            for item in result.scalars():
                object_["type"] = item.type
                object_["password"] = item.password
                object_["og_title"] = item.og_title
                object_["og_url"] = item.og_url
                object_["og_image"] = item.og_image
                object_["og_description"] = item.og_description
                object_["data"] = [
                    (
                        {
                            "object_name": i.data,
                        }
                    ) for i in
                    (
                        item.url if type_ == 1
                        else item.image if type_ == 2
                        else item.video if type_ == 3
                        else []
                    )
                ]
                object_["create_time"] = item.create_time
                object_["expired"] = item.expired
    return object_

async def async_creat_all() -> None:
    engine_gen = db_client.get_async_engine()
    async_engine = await anext(engine_gen)
    
    async with async_engine.begin() as conn:
        await conn.run_sync(schemas.Base.metadata.create_all)
    
if __name__ == "__main__":
    asyncio.run(async_creat_all())