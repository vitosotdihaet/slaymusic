from pydantic import BaseModel, Field
from enum import Enum
import datetime


class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    analyst = "analyst"


class UserID(BaseModel):
    id: int | None = None


class UserUsername(BaseModel):
    username: str


class NewUser(BaseModel):
    name: str
    description: str | None = None
    username: str
    password: str


class LoginUser(BaseModel):
    username: str
    password: str


class FullUser(BaseModel):
    id: int
    username: str
    password: str
    role: UserRole


class NewRoleUser(NewUser):
    role: UserRole


class User(BaseModel):
    id: int
    name: str
    description: str | None = None
    username: str
    role: UserRole
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UpdateUser(BaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    username: str | None = None


class UpdateUserRole(UpdateUser):
    role: UserRole | None = None


class Artist(BaseModel):
    id: int
    name: str
    description: str | None = None


class LoginRegister(BaseModel):
    token: str
    next: str


class UserMiddleware(BaseModel):
    id: int
    role: UserRole


class PlaylistID(BaseModel):
    id: int


class NewPlaylist(BaseModel):
    author_id: int | None = None
    name: str


class Playlist(NewPlaylist):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UpdatePlaylist(BaseModel):
    id: int
    author_id: int | None = None
    name: str | None = None


class PlaylistTrack(BaseModel):
    playlist_id: int
    track_id: int


class SubscribersCount(BaseModel):
    count: int


class Subscribe(BaseModel):
    subscriber_id: int | None = None
    artist_id: int


class AccountsSearchParams(BaseModel):
    name: str | None = None
    skip: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, default=100)
    threshold: float = Field(ge=0, le=1, default=0.3)
    created_search_start: datetime.datetime | None = None
    created_search_end: datetime.datetime | None = None
    updated_search_start: datetime.datetime | None = None
    updated_search_end: datetime.datetime | None = None


class ArtistSearchParams(AccountsSearchParams):
    pass


class UserSearchParams(AccountsSearchParams):
    username: str | None = None


class PlaylistSearchParams(AccountsSearchParams):
    author_id: int | None = None


class SubscribeSearchParams(BaseModel):
    id: int | None = None
    skip: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, default=100)
