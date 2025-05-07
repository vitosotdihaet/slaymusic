from pydantic import BaseModel

class Albums(BaseModel):
    id: int
    artist_id: int
    name: str