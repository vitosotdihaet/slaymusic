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
    Artist,
    Album,
    NewSingle,
    NewTrack,
    TrackID,
    AlbumID,
    ArtistID,
    SearchParams,
)
from services.music import MusicService
from configs.depends import get_music_service
from exceptions.music import (
    InvalidStartException,
    MusicFileNotFoundException,
    MusicBaseException,
    ArtistNotFoundException,
    TrackNotFoundException,
    AlbumNotFoundException,
    ImageFileNotFoundException,
)

router = APIRouter(prefix="/track", tags=["track"])


@router.post("/single", response_model=Track, status_code=status.HTTP_201_CREATED)
async def create_single(
    track: NewSingle = Depends(),
    track_file: UploadFile = File(),
    cover_file: UploadFile | str | None = None,
    music_service: MusicService = Depends(get_music_service),
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
    except MusicBaseException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/", response_model=Track, status_code=status.HTTP_201_CREATED)
async def create_track(
    new_track: NewTrack = Depends(),
    track_file: UploadFile = File(),
    music_service: MusicService = Depends(get_music_service),
):
    data = await track_file.read()
    content_type = track_file.content_type

    try:
        return await music_service.create_track_to_album(new_track, data, content_type)
    except (AlbumNotFoundException, ArtistNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/stream",
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


@router.get("s/by_album", response_model=list[Album])
async def get_track_by_album(
    album_id: AlbumID = Depends(),
    params: SearchParams = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_tracks_by_album(album_id, params)
    except AlbumNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("s/by_artist", response_model=list[Album])
async def get_track_by_artist(
    artist_id: ArtistID = Depends(),
    params: SearchParams = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_tracks_by_artist(artist_id, params)
    except ArtistNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("s/", response_model=list[Artist])
async def get_tracks(
    params: SearchParams = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_tracks(params)
    except MusicBaseException as e:
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
    track: Track = Depends(),
    music_service: MusicService = Depends(get_music_service),
) -> Track:
    try:
        return await music_service.update_track(track)
    except (
        AlbumNotFoundException,
        ArtistNotFoundException,
        TrackNotFoundException,
    ) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/image/", status_code=status.HTTP_200_OK)
async def update_image(
    track_id: TrackID = Depends(),
    cover_file: UploadFile = File(),
    music_service: MusicService = Depends(get_music_service),
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
):
    cover_bytes = await track_file.read()
    cover_content_type = track_file.content_type

    try:
        return await music_service.update_track_file(
            track_id, cover_bytes, cover_content_type
        )
    except (TrackNotFoundException, MusicFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_track(
    track_id: TrackID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        await music_service.delete_track(track_id)
    except TrackNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/image/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_track_image(
    track_id: TrackID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        await music_service.delete_track_image(track_id)
    except (TrackNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
