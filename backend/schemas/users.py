from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    password: str
    # created_at: datetime
    # updated_at: datetime