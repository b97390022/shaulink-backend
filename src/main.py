from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.url_router import router as url_router
from src.config import base_config
import uvicorn

app = FastAPI()

# CORS allowed origins
origins = [
    "https://shaulink.cc",
    "http://localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(url_router, prefix=f"/{base_config.version}")

@app.get("/health", status_code=200)
async def health_check():
    return {"status": "ok"}

    
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)