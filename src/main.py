import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from src.routers.base_router import router as base_router
from src.routers.url_router import router as url_router
from src.routers.image_router import router as image_rourter
from src.config import base_config
from src.db import RedisClient, DBClient
from sqlalchemy.ext.asyncio import AsyncEngine
import src.crud as crud
from src.functions import get_logger
import uvicorn
from typing import Annotated
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from redis.asyncio.client import Redis
from pathlib import Path

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await crud.async_creat_all()
    Path("temp/image").mkdir(parents=True, exist_ok=True)
    Path("temp/video").mkdir(parents=True, exist_ok=True)
    yield
    # cleanup

app = FastAPI(lifespan=lifespan)
redis_client = RedisClient()
db_client = DBClient()

# app.mount("/static", StaticFiles(directory="static"), name="static")
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path.joinpath(BASE_DIR, "static", "templates")))

# CORS allowed origins
origins = [
    "https://shaulink.cc",
    "http://localhost",
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(base_router, prefix=f"/{base_config.version}", tags=["Base"])
app.include_router(url_router, prefix=f"/{base_config.version}", tags=["URL"])
app.include_router(image_rourter, prefix=f"/{base_config.version}", tags=["Image"])


@app.get("/", response_class=HTMLResponse)
async def prerender_root(
    request: Request, 
):
    return templates.TemplateResponse(
        "prerender.html",
        {
            "request": request,
            "og_title": base_config.og_title,
            "og_url": base_config.og_url,
            "og_image": base_config.og_image,
            "og_description": base_config.og_description,
        }
    )

@app.get("/{hash}", response_class=HTMLResponse)
async def prerender_hash(
    request: Request, 
    hash: str,
    user_agent: Annotated[str | None, Header()] = None,
    async_engine: AsyncEngine = Depends(db_client.get_async_engine)
):
    og_title, og_url, og_image, og_description = base_config.og_title, base_config.og_url, base_config.og_image, base_config.og_description
    objects = await crud.get_objects(
        hash,
        await db_client.get_async_session(async_engine)
    )
    if objects:  
        og_title, og_url, og_image, og_description = objects["og_title"], objects["og_url"], objects["og_image"], objects["og_description"]

    return templates.TemplateResponse(
        "prerender.html",
        {
            "request": request,
            "og_title": og_title,
            "og_url": og_url,
            "og_image": og_image,
            "og_description": og_description,
        }
    )
    
@app.get("/health", status_code=200)
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)