from pydantic import BaseModel
from typing import Optional

class Artist(BaseModel):
    id: int
    name: str
    picture: Optional[str] = None