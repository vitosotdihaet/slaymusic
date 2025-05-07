from pydantic import BaseModel

class Tracks(BaseModel):
    id: int
    name: str
    artist_id: int
    album_id: int