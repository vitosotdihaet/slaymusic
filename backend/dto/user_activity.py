import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserActivityPost(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    track_id: int
    event: str


class UserActivity(UserActivityPost):
    id: int
    time: datetime.datetime


class UserActivityFilter(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ids: Optional[list[int]] = None
    user_ids: Optional[list[int]] = None
    track_ids: Optional[list[int]] = None
    events: Optional[list[str]] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None


class TrackPlayedCount(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    track_id: int
    play_count: int


class MostPlayedTracks(BaseModel):
    """
    tracks with play count, sorted by descending play count
    """

    model_config = ConfigDict(from_attributes=True)

    tracks: list[TrackPlayedCount]


class ActiveUsersOnDate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_count: int
    date: datetime.date


class ActiveUsers(BaseModel):
    """
    count of active users per date, sorted by descending date
    """

    model_config = ConfigDict(from_attributes=True)

    entries: list[ActiveUsersOnDate]


class TrackCompletionRate(BaseModel):
    """
    track id and its completion rate (from 0 to 1)
    """

    model_config = ConfigDict(from_attributes=True)

    track_id: int
    completion_rate: float


class TracksCompletionRate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entries: list[TrackCompletionRate]
