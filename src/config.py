from pydantic import BaseModel

base_config = None

class Config(BaseModel):
    version: str = "v1"
    domain: str
    url_ttl: int
    
with open("config.json", "r", encoding="utf-8") as f:
    base_config = Config.model_validate_json(f.read())

assert base_config is not None, "Cannot found config file."