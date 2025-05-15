from pydantic import BaseModel, Field
from typing import AsyncIterator
from dataclasses import dataclass


class MusicFileStats(BaseModel):
    size: int


@dataclass
class TrackStream:
    stream: AsyncIterator[bytes]
    start: int
    end: int
    file_byte_size: int
    content_length: int


class TrackID(BaseModel):
    id: int


class AlbumID(BaseModel):
    id: int


class ArtistID(BaseModel):
    id: int


class NewTrack(BaseModel):
    name: str
    album_id: int
    artist_id: int


class NewArtist(BaseModel):
    name: str
    description: str | None = None


class NewAlbum(BaseModel):
    name: str
    artist_id: int


class NewSingle(NewAlbum):
    pass


class Track(NewTrack):
    id: int


class Artist(NewArtist):
    id: int


class Album(NewAlbum):
    id: int


class SearchParams(BaseModel):
    name: str | None = None
    skip: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, default=100)
    threshold: float = Field(ge=0, le=1, default=0.3)
