from fastapi import APIRouter, HTTPException, Depends, status
from services.accounts import AccountService
from configs.depends import get_accounts_service, check_access
from exceptions.accounts import (
    AccountsBaseException,
    UserAlreadyExist,
    UserNotFoundException,
)
import dto.accounts as dto
from typing import Optional

router = APIRouter(prefix="/accounts", tags=["accounts"])


# оставим тут пока с user_id в path, потом можно из мидлвари доставать
@router.get("/user/{user_id}", response_model=dto.User, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    account_service: AccountService = Depends(get_accounts_service),
    check_access=Depends(check_access),
):
    user: Optional[dto.User] = None
    try:
        user = await account_service.get_user(dto.UserID(id=user_id))
    except AccountsBaseException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return user


@router.post(
    "/register", response_model=dto.LoginRegister, status_code=status.HTTP_201_CREATED
)
async def register(
    user: dto.NewUser, account_service: AccountService = Depends(get_accounts_service)
):
    new_user: Optional[dto.User] = None
    user = dto.NewRoleUser(**user.model_dump(), role=dto.UserRole.user)
    try:
        new_user = await account_service.create_user(user)
    except UserAlreadyExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exist"
        )
    except AccountsBaseException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        new_playlist = dto.NewPlaylist(author_id=new_user.id, name="fav")
        await account_service.create_playlist(new_playlist)
    except Exception:
        err = "something wrong while create fav playlist"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        )

    user_middleware = dto.UserMiddleware(id=new_user.id, is_admin=False)
    access_token = account_service.create_access_token(user_middleware)

    return dto.LoginRegister(token=access_token, next="/home")


@router.post("/login", response_model=dto.LoginRegister, status_code=status.HTTP_200_OK)
async def login(
    login_user: dto.LoginUser,
    account_service: AccountService = Depends(get_accounts_service),
):
    user: Optional[dto.LoginUserWithID] = None
    try:
        user = await account_service.get_user_by_username(
            dto.UserUsername(username=login_user.username)
        )
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not account_service.verify_password(login_user.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    user_middleware = dto.UserMiddleware(id=user.id, is_admin=False)
    access_token = account_service.create_access_token(user_middleware)

    return dto.LoginRegister(token=access_token, next="/home")
