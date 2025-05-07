from fastapi import (
    APIRouter,
    UploadFile,
    HTTPException,
    status,
    Depends,
    Request,
)
from fastapi.responses import StreamingResponse

from entities.music import Music
from services.music import MusicService
from depends import get_music_service
from services.exceptions import (
    InvalidStartException,
    MusicFileNotFoundException,
    UseCaseException,
)

router = APIRouter(prefix="/music", tags=["music"])


@router.get(
    "/{music_name}",
    response_model=None,
    status_code=206,
)
async def stream_music_endpoint(
    music_name: str,
    request: Request,
    music_service: MusicService = Depends(get_music_service),
) -> StreamingResponse:
    range_header = request.headers.get("Range")
    start = None
    end = None
    if range_header:
        range_type, range_spec = range_header.split("=")
        if range_type.strip() != "bytes":
            raise HTTPException(status_code=400, detail="Invalid range type")

        range_parts = range_spec.split("-")
        start = int(range_parts[0]) if range_parts[0] else None
        end = int(range_parts[1]) if range_parts[1] else None

    try:
        music = await music_service.stream_music(music_name, start, end)
    except InvalidStartException as e:
        raise HTTPException(
            status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, detail=str(e)
        )
    except MusicFileNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return StreamingResponse(
        music.music_stream,
        status_code=206,
        media_type="audio/mpeg",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {music.start}-{music.end}/{music.file_byte_size}",
            "Content-Length": str(music.content_length),
        },
    )


@router.post("/", response_model=None, status_code=201)
async def create_music(
    name: str,
    artist: str,
    music_file: UploadFile,
    album: str | None = None,
    cover_file: UploadFile | str | None = None,
    music_service: MusicService = Depends(get_music_service),
):
    data = await music_file.read()
    content_type = music_file.content_type

    if cover_file == "":
        cover_file = None
    cover_path = None
    if cover_file:
        cover_bytes = await cover_file.read()
        cover_content_type = cover_file.content_type
        cover_path = cover_file.filename

    music = Music(
        name=name,
        artist=artist,
        album=album,
        cover_file_path=cover_path,
    )
    try:
        await music_service.create_music(music, data, content_type)
        if cover_file:
            await music_service.create_cover(music, cover_bytes, cover_content_type)
    except UseCaseException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{music_name}/metadata", response_model=Music)
async def read_metadata(
    music_name: str,
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_metadata(music_name)
    except UseCaseException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{music_name}/metadata", status_code=204)
async def update_metadata(
    music_name: str,
    meta: Music,
    music_service: MusicService = Depends(get_music_service),
):
    try:
        await music_service.update_metadata(music_name, meta)
    except UseCaseException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{music_name}", status_code=200)
async def delete_music(
    music_name: str,
    music_service: MusicService = Depends(get_music_service),
):
    try:
        await music_service.delete_music(music_name)
    except MusicFileNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
