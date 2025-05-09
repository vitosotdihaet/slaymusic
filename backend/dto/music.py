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


class NewTrack(BaseModel):
    name: str
    album_id: int
    artist_id: int


class NewArtist(BaseModel):
    name: str
    description: str | None


class NewAlbum(BaseModel):
    name: str
    artist_id: int


class Track(BaseModel):
    id: int
    name: str
    album_id: int
    artist_id: int


class Artist(BaseModel):
    id: int
    name: str
    description: str | None


class Album(BaseModel):
    id: int
    name: str
    artist_id: int
