from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    status,
    Depends,
)
from fastapi.responses import Response
from dto.music import NewAlbum, Album, AlbumID, ArtistID, SearchParams
from services.music import MusicService
from configs.depends import get_music_service
from exceptions.music import (
    MusicBaseException,
    AlbumNotFoundException,
    ImageFileNotFoundException,
    ArtistNotFoundException,
)

router = APIRouter(prefix="/album", tags=["album"])


@router.post(
    "/",
    response_model=Album,
    status_code=status.HTTP_201_CREATED,
)
async def create_album(
    new_album: NewAlbum = Depends(),
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
        return await music_service.create_album(
            new_album, cover_bytes, cover_content_type
        )
    except MusicBaseException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=Album)
async def get_album(
    album_id: AlbumID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_album(album_id)
    except AlbumNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("s/by_artist", response_model=list[Album])
async def get_albums_by_artist(
    artist_id: ArtistID = Depends(),
    params: SearchParams = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_albums_by_artist(artist_id, params)
    except ArtistNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("s/", response_model=list[Album])
async def get_albums(
    params: SearchParams = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_albums(params)
    except MusicBaseException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/image", responses={200: {"content": {"image/png": {}}}}, response_class=Response
)
async def get_album_image(
    album_id: AlbumID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        image_bytes = await music_service.get_album_image(album_id)
        return Response(content=image_bytes, media_type="image/png")
    except (AlbumNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/", response_model=Album)
async def update_metadata(
    album: Album = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.update_album(album)
    except (AlbumNotFoundException, ArtistNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/image/", status_code=status.HTTP_200_OK)
async def update_image(
    album_id: AlbumID = Depends(),
    cover_file: UploadFile = File(),
    music_service: MusicService = Depends(get_music_service),
):
    cover_bytes = await cover_file.read()
    cover_content_type = cover_file.content_type

    try:
        return await music_service.update_album_image(
            album_id, cover_bytes, cover_content_type
        )
    except (AlbumNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album(
    album_id: AlbumID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        await music_service.delete_album(album_id)
    except AlbumNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/image/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album_image(
    album_id: AlbumID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        await music_service.delete_album_image(album_id)
    except (AlbumNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
