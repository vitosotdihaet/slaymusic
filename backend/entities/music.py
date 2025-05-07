from pydantic import BaseModel
from typing import Optional


class Music(BaseModel):
    name: str
    artist: str
    album: Optional[str] = None
    cover_file_path: Optional[str] = None
