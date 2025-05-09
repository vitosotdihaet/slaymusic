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
    track_name: str
    picture_path: str


class Artist(BaseModel):
    artist_name: str
    artist_picture_path: str


class Album(BaseModel):
    album_name: str
    picture_path: str
