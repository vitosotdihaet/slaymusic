from fastapi import (
    APIRouter,
    UploadFile,
    HTTPException,
    status,
    Depends,
    Request,
)
from fastapi.responses import StreamingResponse
from dto.music import Track, NewArtist, Artist, NewAlbum, Album
from services.music import MusicService
from configs.depends import get_music_service
from exceptions.music import (
    InvalidStartException,
    MusicFileNotFoundException,
    UseCaseException,
)

router = APIRouter(prefix="/music", tags=["music"])


@router.post(
    "/artists",
    response_model=None,
    status_code=201,
)
async def create_artist(
    artist_name: str,
    artist_description: str | None,
    music_service: MusicService = Depends(get_music_service),
):
    artist = NewArtist(name=artist_name, description=artist_description)
    try:
        await music_service.create_artist(artist)
        # if cover_file:
        #     await music_service.create_cover(music, cover_bytes, cover_content_type)
    except UseCaseException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/artists/{artist_id}", response_model=Artist)
async def get_artist(
    artist_id: int,
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_artist(artist_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Artist not found")


@router.delete("/artists/{artist_id}", status_code=200)
async def delete_artist(
    artist: Artist,
    music_service: MusicService = Depends(get_music_service),
):
    try:
        await music_service.delete_artist(artist)
    except MusicFileNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/artists/{artist_id}", status_code=204)
async def update_metadata(
    artist_id: int,
    artist: Artist,
    music_service: MusicService = Depends(get_music_service),
):
    try:
        await music_service.update_artist(artist_id, artist)
    except UseCaseException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/albums",
    response_model=None,
    status_code=201,
)
async def create_album(
    name: str,
    artist_id: int,
    music_service: MusicService = Depends(get_music_service),
):
    album = NewAlbum(name=name, artist_id=artist_id)
    try:
        await music_service.create_album(album)
        # if cover_file:
        #     await music_service.create_cover(music, cover_bytes, cover_content_type)
    except UseCaseException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/albums/{album_id}", response_model=Album)
async def get_album(
    album_id: int,
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_album(album_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Artist not found")


@router.delete("/albums/{album_id}", status_code=200)
async def delete_album(
    album: Album,
    music_service: MusicService = Depends(get_music_service),
):
    try:
        await music_service.delete_album(album)
    except MusicFileNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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

    music = Track(
        name=name,
        artist=artist,
        album=album,
        picture_path=cover_path,
    )
    try:
        await music_service.create_music(music, data, content_type)
        if cover_file:
            await music_service.create_cover(music, cover_bytes, cover_content_type)
    except UseCaseException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{music_id}",
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
