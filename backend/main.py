from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from minio import Minio
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    minio_port: str 
    minio_root_user: str  
    minio_root_password: str  

    @field_validator("*", mode="before")
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


settings = Settings()

minio_client = Minio(
    'minio-service:' + settings.minio_port,
    access_key=settings.minio_root_user, 
    secret_key=settings.minio_root_password,
    secure=False
)
app = FastAPI()

@app.get("/music")
async def play_music(request: Request):
    file_byte_size = minio_client.stat_object("music", "Palace - Vision - Original Mix.mp3").size
 
    range_header = request.headers.get("Range")
    range_type, range_spec = range_header.split("=")
    if range_type.strip() != "bytes":
        raise HTTPException(status_code=400, detail="Invalid range type")

    range_parts = range_spec.split("-")
    start = int(range_parts[0]) if range_parts[0] else 0
    end = int(range_parts[1]) if range_parts[1] else file_byte_size - 1

    if start >= file_byte_size:
        raise HTTPException(status_code=416, detail="Requested range not satisfiable")
    
    end = min(end, file_byte_size - 1)
    content_length = end - start + 1

    response = minio_client.get_object("music", "Palace - Vision - Original Mix.mp3", start, content_length)

    return StreamingResponse(
        response.stream(),
        status_code=206, 
        media_type="audio/mpeg",
        headers={
            'Accept-Ranges': 'bytes',
            'Content-Range': f'bytes {start}-{end}/{file_byte_size}',
            'Content-Length': str(content_length),
        }
    )  