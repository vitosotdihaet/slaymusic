from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    status,
    Depends,
    Request,
)
from fastapi.responses import StreamingResponse, Response
from dto.music import (
    Track,
    NewSingle,
    NewTrack,
    TrackID,
    TrackSearchParams,
    UpdateTrack,
)
from dto.accounts import UserMiddleware
from services.music import MusicService
from configs.depends import (
    get_music_service,
    get_owner_or_admin,
    require_owner_or_admin,
)
from exceptions.music import (
    InvalidStartException,
    MusicFileNotFoundException,
    TrackNotFoundException,
    AlbumNotFoundException,
    ImageFileNotFoundException,
    GenreNotFoundException,
)
from exceptions.accounts import UserNotFoundException

router = APIRouter(prefix="/track", tags=["track"])


@router.post("/single/", response_model=Track, status_code=status.HTTP_201_CREATED)
async def create_single(
    _: NewSingle = Depends(),
    track_file: UploadFile = File(),
    cover_file: UploadFile | str | None = None,
    music_service: MusicService = Depends(get_music_service),
    track: UserMiddleware = Depends(get_owner_or_admin(NewSingle, "artist_id")),
):
    data = await track_file.read()
    content_type = track_file.content_type

    cover_bytes = None
    cover_content_type = None
    if cover_file == "":
        cover_file = None
    if cover_file:
        cover_bytes = await cover_file.read()
        cover_content_type = cover_file.content_type

    try:
        return await music_service.create_track_single(
            track, data, content_type, cover_bytes, cover_content_type
        )
    except (GenreNotFoundException, UserNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/", response_model=Track, status_code=status.HTTP_201_CREATED)
async def create_track(
    _: NewTrack = Depends(),
    track_file: UploadFile = File(),
    music_service: MusicService = Depends(get_music_service),
    new_track: UserMiddleware = Depends(get_owner_or_admin(NewTrack, "artist_id")),
):
    data = await track_file.read()
    content_type = track_file.content_type

    try:
        return await music_service.create_track_to_album(new_track, data, content_type)
    except (
        AlbumNotFoundException,
        UserNotFoundException,
        GenreNotFoundException,
    ) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/stream/",
    response_model=None,
    status_code=206,
)
async def stream_track(
    request: Request,
    track_id: TrackID = Depends(),
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
        track_stream = await music_service.stream_track(track_id, start, end)
    except InvalidStartException as e:
        raise HTTPException(
            status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, detail=str(e)
        )
    except TrackNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return StreamingResponse(
        track_stream.stream,
        status_code=206,
        media_type="audio/mpeg",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {track_stream.start}-{track_stream.end}/{track_stream.file_byte_size}",
            "Content-Length": str(track_stream.content_length),
        },
    )


@router.get("/", response_model=Track)
async def get_track(
    track_id: TrackID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_track(track_id)
    except TrackNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("s/", response_model=list[Track])
async def get_tracks(
    params: TrackSearchParams = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_tracks(params)
    except (
        UserNotFoundException,
        AlbumNotFoundException,
        GenreNotFoundException,
    ) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/image/", responses={200: {"content": {"image/png": {}}}}, response_class=Response
)
async def get_image(
    track_id: TrackID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        image_bytes = await music_service.get_track_image(track_id)
        return Response(content=image_bytes, media_type="image/png")
    except (TrackNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/", response_model=Track)
async def update_track(
    track: UpdateTrack = Depends(),
    music_service: MusicService = Depends(get_music_service),
    _: UserMiddleware = Depends(
        require_owner_or_admin(UpdateTrack, "id", "get_track", get_music_service)
    ),
) -> Track:
    try:
        return await music_service.update_track(track)
    except (
        AlbumNotFoundException,
        UserNotFoundException,
        TrackNotFoundException,
        GenreNotFoundException,
    ) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/image/", status_code=status.HTTP_200_OK)
async def update_image(
    track_id: TrackID = Depends(),
    cover_file: UploadFile = File(),
    music_service: MusicService = Depends(get_music_service),
    _: UserMiddleware = Depends(
        require_owner_or_admin(TrackID, "id", "get_track", get_music_service)
    ),
):
    cover_bytes = await cover_file.read()
    cover_content_type = cover_file.content_type

    try:
        return await music_service.update_track_image(
            track_id, cover_bytes, cover_content_type
        )
    except (TrackNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/file/", status_code=status.HTTP_200_OK)
async def update_track_file(
    track_id: TrackID = Depends(),
    track_file: UploadFile = File(),
    music_service: MusicService = Depends(get_music_service),
    _: UserMiddleware = Depends(
        require_owner_or_admin(TrackID, "id", "get_track", get_music_service)
    ),
):
    file_bytes = await track_file.read()
    file_content_type = track_file.content_type

    try:
        return await music_service.update_track_file(
            track_id, file_bytes, file_content_type
        )
    except (
        TrackNotFoundException,
        MusicFileNotFoundException,
        GenreNotFoundException,
    ) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_track(
    track_id: TrackID = Depends(),
    music_service: MusicService = Depends(get_music_service),
    _: UserMiddleware = Depends(
        require_owner_or_admin(TrackID, "id", "get_track", get_music_service)
    ),
):
    try:
        await music_service.delete_track(track_id)
    except TrackNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/image/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_track_image(
    track_id: TrackID = Depends(),
    music_service: MusicService = Depends(get_music_service),
    _: UserMiddleware = Depends(
        require_owner_or_admin(TrackID, "id", "get_track", get_music_service)
    ),
):
    try:
        await music_service.delete_track_image(track_id)
    except (TrackNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
