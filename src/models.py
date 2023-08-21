from pydantic import BaseModel
from pydantic import HttpUrl

class UrlItem(BaseModel):
    url: HttpUrl

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://www.yahoo.com.tw",
                }
            ]
        }
    }