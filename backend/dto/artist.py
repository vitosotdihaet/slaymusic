from pydantic import BaseModel

class Artists(BaseModel):
    id: int
    name: str
