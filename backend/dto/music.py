from datetime import date, datetime
from fastapi import Query
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


class GenreID(BaseModel):
    id: int


class AlbumID(BaseModel):
    id: int


class TrackID(BaseModel):
    id: int = Query(ge=0)


class NewGenre(BaseModel):
    name: str


class UpdateGenre(BaseModel):
    id: int
    name: str


class NewAlbum(BaseModel):
    name: str
    artist_id: int | None = None
    release_date: date


class UpdateAlbum(BaseModel):
    id: int
    name: str | None = None
    artist_id: int | None = None
    release_date: date | None = None


class NewSingle(BaseModel):
    name: str
    artist_id: int | None = None
    genre_id: int | None = None
    release_date: date


class NewTrack(BaseModel):
    name: str
    album_id: int
    artist_id: int | None = None
    genre_id: int | None = None
    release_date: date


class UpdateTrack(BaseModel):
    id: int
    name: str | None = None
    album_id: int | None = None
    artist_id: int | None = None
    genre_id: int | None = None
    release_date: date | None = None


class Genre(NewGenre):
    id: int
    created_at: datetime
    updated_at: datetime


class Album(NewAlbum):
    id: int
    created_at: datetime
    updated_at: datetime


class Track(NewTrack):
    id: int
    created_at: datetime
    updated_at: datetime


class MusicSearchParams(BaseModel):
    name: str | None = None
    skip: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, default=100)
    threshold: float = Field(ge=0, le=1, default=0.3)
    created_search_start: datetime | None = None
    created_search_end: datetime | None = None
    updated_search_start: datetime | None = None
    updated_search_end: datetime | None = None


class GenreSearchParams(MusicSearchParams):
    pass


class AlbumSearchParams(MusicSearchParams):
    artist_id: int | None = None
    release_search_start: date | None = None
    release_search_end: date | None = None


class TrackSearchParams(MusicSearchParams):
    artist_id: int | None = None
    playlist_id: int | None = None
    album_id: int | None = None
    genre_id: int | None = None
    release_search_start: date | None = None
    release_search_end: date | None = None
