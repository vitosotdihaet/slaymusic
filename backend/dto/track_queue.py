from fastapi import Query
from pydantic import BaseModel, ConfigDict


class InQueueID(BaseModel):
    """
    index of an element in a queue-holding datastructure
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Query(ge=0)


class QueueParameters(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    offset: int = Query(ge=0, default=0)
    limit: int = Query(ge=0, default=10)


class TrackQueue(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    track_ids: list[int]


class TrackInQueueIDs(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    track_id: int = Query(ge=0)
    queue_id: int = Query(ge=0)


class QueueSrcDestIDs(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    src_id: int = Query(ge=0)
    dest_id: int = Query(ge=0)
