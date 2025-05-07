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
