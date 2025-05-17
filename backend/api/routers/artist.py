from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    status,
    Depends,
)
from fastapi.responses import Response
from dto.music import NewArtist, Artist, ArtistID, ArtistSearchParams
from services.music import MusicService
from configs.depends import get_music_service
from exceptions.music import (
    MusicBaseException,
    ArtistNotFoundException,
    ImageFileNotFoundException,
)

router = APIRouter(prefix="/artist", tags=["artist"])


@router.post(
    "/",
    response_model=Artist,
    status_code=status.HTTP_201_CREATED,
)
async def create_artist(
    new_artist: NewArtist = Depends(),
    cover_file: UploadFile | str | None = None,
    music_service: MusicService = Depends(get_music_service),
):
    cover_bytes = None
    cover_content_type = None
    if cover_file == "":
        cover_file = None
    if cover_file:
        cover_bytes = await cover_file.read()
        cover_content_type = cover_file.content_type

    try:
        return await music_service.create_artist(
            new_artist, cover_bytes, cover_content_type
        )
    except MusicBaseException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=Artist)
async def get_artist(
    artist_id: ArtistID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_artist(artist_id)
    except ArtistNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("s/", response_model=list[Artist])
async def get_artists(
    params: ArtistSearchParams = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_artists(params)
    except ArtistNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/image/", responses={200: {"content": {"image/png": {}}}}, response_class=Response
)
async def get_image(
    artist_id: ArtistID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        image_bytes = await music_service.get_artist_image(artist_id)
        return Response(content=image_bytes, media_type="image/png")
    except (ArtistNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/", response_model=Artist)
async def update_metadata(
    artist: Artist = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.update_artist(artist)
    except ArtistNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/image/", status_code=status.HTTP_200_OK)
async def update_image(
    artist_id: ArtistID = Depends(),
    cover_file: UploadFile = File(),
    music_service: MusicService = Depends(get_music_service),
):
    cover_bytes = await cover_file.read()
    cover_content_type = cover_file.content_type

    try:
        return await music_service.update_artist_image(
            artist_id, cover_bytes, cover_content_type
        )
    except (ArtistNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artist(
    artist_id: ArtistID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        await music_service.delete_artist(artist_id)
    except ArtistNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/image/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artist_image(
    artist_id: ArtistID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        await music_service.delete_artist_image(artist_id)
    except (ArtistNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
