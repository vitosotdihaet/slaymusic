from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import Optional
from fastapi.responses import Response

from services.accounts import AccountService
from configs.depends import (
    get_account_service,
    get_owner_or_admin,
    get_owner_or_user,
    check_admin_access,
)
from exceptions.accounts import (
    AccountsBaseException,
    UserAlreadyExist,
    UserNotFoundException,
)
from exceptions.music import (
    ImageFileNotFoundException,
)
from dto.accounts import (
    User,
    UserID,
    UserMiddleware,
    UserRole,
    UserSearchParams,
    ArtistSearchParams,
    UserUsername,
    NewUser,
    FullUser,
    LoginUser,
    NewRoleUser,
    LoginRegister,
    NewPlaylist,
    Artist,
    UpdateUser,
    UpdateUserRole,
)


router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/register/", response_model=LoginRegister, status_code=status.HTTP_201_CREATED
)
async def register(
    user: NewUser = Depends(),
    cover_file: UploadFile | str | None = None,
    account_service: AccountService = Depends(get_account_service),
):
    cover_bytes = None
    cover_content_type = None
    if cover_file == "":
        cover_file = None
    if cover_file:
        cover_bytes = await cover_file.read()
        cover_content_type = cover_file.content_type

    new_user: Optional[User] = None
    user = NewRoleUser(**user.model_dump(), role=UserRole.user)
    try:
        new_user = await account_service.create_user(
            user, cover_bytes, cover_content_type
        )
    except UserAlreadyExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exist"
        )
    except AccountsBaseException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        new_playlist = NewPlaylist(author_id=new_user.id, name="fav")
        await account_service.create_playlist(new_playlist)
    except AccountsBaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="something went wrong while creating 'favorites' playlist: "
            + str(e),
        )

    user_middleware = UserMiddleware(id=new_user.id, role=UserRole.user)
    access_token = account_service.create_access_token(user_middleware)

    return LoginRegister(token=access_token, next="/home")


@router.get("/", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(
    _: UserID = Depends(),
    account_service: AccountService = Depends(get_account_service),
    user: UserMiddleware = Depends(get_owner_or_admin(UserID, "id")),
):
    try:
        return await account_service.get_user(user)
    except AccountsBaseException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("s/", response_model=list[User])
async def get_users(
    params: UserSearchParams = Depends(),
    account_service: AccountService = Depends(get_account_service),
    _: UserMiddleware = Depends(check_admin_access),
):
    try:
        return await account_service.get_users(params)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/artist/", response_model=Artist)
async def get_artist(
    _: UserID = Depends(),
    account_service: AccountService = Depends(get_account_service),
    user_id: UserMiddleware = Depends(get_owner_or_user(UserID, "id")),
):
    try:
        return await account_service.get_user_artist(user_id)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("s/artist/", response_model=list[Artist])
async def get_artists(
    params: ArtistSearchParams = Depends(),
    account_service: AccountService = Depends(get_account_service),
):
    try:
        return await account_service.get_users_artists(params)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/image/", responses={200: {"content": {"image/png": {}}}}, response_class=Response
)
async def get_image(
    _: UserID = Depends(),
    account_service: AccountService = Depends(get_account_service),
    user_id: UserMiddleware = Depends(get_owner_or_user(UserID, "id")),
):
    try:
        image_bytes = await account_service.get_user_image(user_id)
        return Response(content=image_bytes, media_type="image/png")
    except (UserNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/login/", response_model=LoginRegister, status_code=status.HTTP_200_OK)
async def login(
    login_user: LoginUser = Depends(),
    account_service: AccountService = Depends(get_account_service),
):
    user: Optional[FullUser] = None
    try:
        user = await account_service.get_user_by_username(
            UserUsername(username=login_user.username)
        )
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not account_service.verify_password(login_user.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    user_middleware = UserMiddleware(id=user.id, role=user.role)
    access_token = account_service.create_access_token(user_middleware)

    return LoginRegister(token=access_token, next="/home")


@router.put("/", response_model=User)
async def update_metadata(
    _: UpdateUser = Depends(),
    account_service: AccountService = Depends(get_account_service),
    user: UserMiddleware = Depends(get_owner_or_admin(UpdateUser, "id")),
):
    try:
        return await account_service.update_user(user)
    except (UserNotFoundException, UserAlreadyExist) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/admin/", response_model=User)
async def update_metadata_with_role(
    params: UpdateUserRole = Depends(),
    account_service: AccountService = Depends(get_account_service),
    _: UserMiddleware = Depends(check_admin_access),
):
    try:
        return await account_service.update_user(params)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/image/", status_code=status.HTTP_200_OK)
async def update_image(
    _: UserID = Depends(),
    cover_file: UploadFile = File(),
    account_service: AccountService = Depends(get_account_service),
    user: UserMiddleware = Depends(get_owner_or_admin(UserID, "id")),
):
    cover_bytes = await cover_file.read()
    cover_content_type = cover_file.content_type

    try:
        return await account_service.update_user_image(
            user, cover_bytes, cover_content_type
        )
    except (UserNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    _: UserID = Depends(),
    account_service: AccountService = Depends(get_account_service),
    user: UserMiddleware = Depends(get_owner_or_admin(UserID, "id")),
):
    try:
        await account_service.delete_user(user)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/image/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_image(
    _: UserID = Depends(),
    account_service: AccountService = Depends(get_account_service),
    user: UserMiddleware = Depends(get_owner_or_admin(UserID, "id")),
):
    try:
        await account_service.delete_user_image(user)
    except (UserNotFoundException, ImageFileNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
