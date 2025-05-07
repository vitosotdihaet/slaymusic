from pydantic import BaseModel
from typing import Optional

class Album(BaseModel):
    id: int
    artist_id: int
    name: str
    picture: Optional[str] = None