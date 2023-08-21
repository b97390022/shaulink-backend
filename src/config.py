from pydantic import BaseModel

base_config = None

class ObjectStorage(BaseModel):
    hostname: str
    access_key: str
    secret_key: str

class Config(BaseModel):
    version: str = "v1"
    domain: str
    port: int
    url_ttl: int
    og_title: str = "Shaulink - The BEST URL Shortener"
    og_url: str = "https://shaulink.cc"
    og_image: str = "https://shaulink.cc/apple-touch-icon.png"
    og_description: str = "This is a SIMPLE and FAST URL Shortener."
    object_storage: ObjectStorage

with open("config.json", "r", encoding="utf-8") as f:
    base_config = Config.model_validate_json(f.read())

assert base_config is not None, "Cannot found config file."