from datetime import date
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


class ArtistID(BaseModel):
    id: int


class AlbumID(BaseModel):
    id: int


class TrackID(BaseModel):
    id: int = Query(ge=0)


class NewGenre(BaseModel):
    name: str


class NewArtist(BaseModel):
    name: str
    description: str | None = None


class NewAlbum(BaseModel):
    name: str
    artist_id: int
    release_date: date


class NewSingle(BaseModel):
    name: str
    artist_id: int
    genre_id: int | None = None
    release_date: date


class NewTrack(BaseModel):
    name: str
    album_id: int
    artist_id: int
    genre_id: int | None = None
    release_date: date


class Genre(NewGenre):
    id: int


class Artist(NewArtist):
    id: int


class Album(NewAlbum):
    id: int


class Track(NewTrack):
    id: int


class SearchParams(BaseModel):
    name: str | None = None
    skip: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, default=100)
    threshold: float = Field(ge=0, le=1, default=0.3)


class GenreSearchParams(SearchParams):
    pass


class ArtistSearchParams(SearchParams):
    pass


class AlbumSearchParams(SearchParams):
    artist_id: int | None = None
    search_start: date | None = None
    search_end: date | None = None


class TrackSearchParams(SearchParams):
    artist_id: int | None = None
    album_id: int | None = None
    genre_id: int | None = None
    search_start: date | None = None
    search_end: date | None = None
