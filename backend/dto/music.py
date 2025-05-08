from pydantic import BaseModel
from typing import AsyncIterator
from dataclasses import dataclass


class MusicStats(BaseModel):
    size: int


@dataclass
class MusicStream:
    music_stream: AsyncIterator[bytes]
    start: int
    end: int
    file_byte_size: int
    content_length: int


class Track(BaseModel):
    id: int
    name: str
    artist_id: int
    album_id: int
    picture_path: str


class Artist(BaseModel):
    id: int
    name: str
    picture_path: str


class Album(BaseModel):
    id: int
    artist_id: int
    name: str
    picture_path: str
