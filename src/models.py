from pydantic import BaseModel
from pydantic import HttpUrl

class UrlItem(BaseModel):
    url: HttpUrl