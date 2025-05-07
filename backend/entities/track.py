from pydantic import BaseModel
from typing import Optional

class Track(BaseModel):
    id: int
    name: str
    artist_id: int
    album_id: int
    audio: Optional[str] = None