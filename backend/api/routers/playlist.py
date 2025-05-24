from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    status,
    Depends,
)
from fastapi.responses import Response

from dto.accounts import (
    NewPlaylist,
    Playlist,
    PlaylistID,
    PlaylistSearchParams,
    PlaylistTrack,
    UpdatePlaylist,
    UserMiddleware,
)
from services.accounts import AccountService
from configs.depends import (
    get_account_service,
    require_owner_or_admin,
    get_owner_or_admin,
)
from exceptions.accounts import (
    UserNotFoundException,
    PlaylistNotFoundException,
    PlaylistTrackNotFoundException,
    PlaylistAlreadyExist,
)
from exceptions.music import ImageFileNotFoundException, TrackNotFoundException

router = APIRouter(prefix="/playlist", tags=["playlist"])


@router.post(
    "/",
    response_model=Playlist,
    status_code=status.HTTP_201_CREATED,
)
async def create_playlist(
    _: NewPlaylist = Depends(),
    image_file: UploadFile | str | None = None,
    accounts_service: AccountService = Depends(get_account_service),
    new_playlist: UserMiddleware = Depends(
        get_owner_or_admin(NewPlaylist, "author_id")
    ),
):
    image_bytes = None
    image_content_type = None
    if image_file == "":
        image_file = None
    if image_file:
        image_bytes = await image_file.read()
        image_content_type = image_file.content_type

    try:
        return await accounts_service.create_playlist(
            new_playlist, image_bytes, image_content_type
        )
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=Playlist)
async def get_playlist(
    playlist_id: PlaylistID = Depends(),
    accounts_service: AccountService = Depends(get_account_service),
):
    try:
        return await accounts_service.get_playlist(playlist_id)
    except PlaylistNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("s/", response_model=list[Playlist])
async def get_playlists(
    params: PlaylistSearchParams = Depends(),
    accounts_service: AccountService = Depends(get_account_service),
):
    try:
        return await accounts_service.get_playlists(params)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/image/",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def get_image(
    playlist_id: PlaylistID = Depends(),
    accounts_service: AccountService = Depends(get_account_service),
):
    try:
        image_bytes = await accounts_service.get_playlist_image(playlist_id)
        return Response(content=image_bytes, media_type="image/png")
    except (PlaylistNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/", response_model=Playlist)
async def update_metadata(
    playlist: UpdatePlaylist = Depends(),
    accounts_service: AccountService = Depends(get_account_service),
    _: UserMiddleware = Depends(
        require_owner_or_admin(
            UpdatePlaylist, "id", "get_playlist", get_account_service
        )
    ),
):
    try:
        return await accounts_service.update_playlist(playlist)
    except (UserNotFoundException, PlaylistNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/image/", status_code=status.HTTP_200_OK)
async def update_playlist_image(
    playlist_id: PlaylistID = Depends(),
    image_file: UploadFile = File(),
    accounts_service: AccountService = Depends(get_account_service),
    _: UserMiddleware = Depends(
        require_owner_or_admin(PlaylistID, "id", "get_playlist", get_account_service)
    ),
):
    image_bytes = await image_file.read()
    image_content_type = image_file.content_type

    try:
        return await accounts_service.update_playlist_image(
            playlist_id, image_bytes, image_content_type
        )
    except (PlaylistNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(
    playlist_id: PlaylistID = Depends(),
    accounts_service: AccountService = Depends(get_account_service),
    _: UserMiddleware = Depends(
        require_owner_or_admin(PlaylistID, "id", "get_playlist", get_account_service)
    ),
):
    try:
        await accounts_service.delete_playlist(playlist_id)
    except PlaylistNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/image/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    playlist_id: PlaylistID = Depends(),
    accounts_service: AccountService = Depends(get_account_service),
    _: UserMiddleware = Depends(
        require_owner_or_admin(PlaylistID, "id", "get_playlist", get_account_service)
    ),
):
    try:
        await accounts_service.delete_playlist_image(playlist_id)
    except (PlaylistNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# === Playlist-Track endpoints ===


@router.post(
    "/track/",
    response_model=PlaylistTrack,
    status_code=status.HTTP_201_CREATED,
)
async def add_track_to_playlist(
    playlist_track: PlaylistTrack = Depends(),
    accounts_service: AccountService = Depends(get_account_service),
    user_data: UserMiddleware = Depends(
        require_owner_or_admin(
            PlaylistTrack, "playlist_id", "get_playlist", get_account_service
        )
    ),
):
    try:
        return await accounts_service.add_track_to_playlist(playlist_track)
    except (
        PlaylistNotFoundException,
        TrackNotFoundException,
    ) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PlaylistAlreadyExist as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/track/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_track_from_playlist(
    playlist_track: PlaylistTrack = Depends(),
    accounts_service: AccountService = Depends(get_account_service),
    user_data: UserMiddleware = Depends(
        require_owner_or_admin(
            PlaylistTrack, "playlist_id", "get_playlist", get_account_service
        )
    ),
):
    try:
        await accounts_service.remove_track_from_playlist(playlist_track)
    except (
        PlaylistNotFoundException,
        PlaylistTrackNotFoundException,
        TrackNotFoundException,
    ) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
