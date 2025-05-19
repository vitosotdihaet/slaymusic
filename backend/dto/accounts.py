from pydantic import BaseModel
from enum import Enum
import datetime


class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    analyst = "analyst"


class UserID(BaseModel):
    id: int


class UserUsername(BaseModel):
    username: str


class NewUser(BaseModel):
    name: str
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
    username: str
    role: UserRole
    created_at: datetime.datetime
    updated_at: datetime.datetime


class LoginRegister(BaseModel):
    token: str
    next: str


class UserMiddleware(BaseModel):
    id: int
    role: UserRole


class PlaylistID(BaseModel):
    playlist_id: int


class NewPlaylist(BaseModel):
    author_id: int
    name: str


class Playlist(BaseModel):
    playlist_id: int
    author_id: int
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class NewPlaylistTrack(BaseModel):
    playlist_id: int
    track_id: int


class PlaylistTrack(BaseModel):
    playlist_id: int
    track_id: int
