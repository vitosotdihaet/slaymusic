from datetime import datetime
from beanie import Document
from pydantic import Field


class UserActivityModel(Document):
    user_id: int
    track_id: int
    event: str = Field(max_length=20)
    time: datetime = Field(default_factory=datetime.now)
