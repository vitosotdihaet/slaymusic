from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    name: str
    password: str
    created_at: datetime = None
    updated_at: datetime = None

class UserCreated(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
