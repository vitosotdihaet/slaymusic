from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from configs.depends import (
    get_account_service,
    check_access,
    require_owner_or_admin,
)
from dto.accounts import (
    UserID,
    SubscribersCount,
    UserMiddleware,
    Subscribe,
    Artist,
    SubscribeSearchParams,
)
from services.accounts import AccountService
from exceptions.accounts import (
    UserNotFoundException,
    SubscriptionNotFoundException,
    SubscriptionAlreadyExist,
)

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/subscribe",
    status_code=status.HTTP_201_CREATED,
)
async def subscribe_to(
    subscribe: Subscribe = Depends(),
    # user_data: UserMiddleware = Depends(
    #     require_owner_or_admin(Subscribe, "subscriber_id")
    # ),
    account_service: AccountService = Depends(get_account_service),
):
    if subscribe.subscriber_id == subscribe.artist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot subscribe to self"
        )
    try:
        await account_service.subscribe_to(subscribe)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SubscriptionAlreadyExist as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_from(
    subscribe: Subscribe = Depends(),
    account_service: AccountService = Depends(get_account_service),
    # user_data: UserMiddleware = Depends(check_access),
):
    try:
        await account_service.unsubscribe_from(subscribe)
    except (UserNotFoundException, SubscriptionNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/subscriptions", response_model=List[Artist])
async def get_subscriptions(
    params: SubscribeSearchParams = Depends(),
    account_service: AccountService = Depends(get_account_service),
    # user_data: UserMiddleware = Depends(check_access),
):
    try:
        return await account_service.get_subscriptions(params)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/subscribers", response_model=List[Artist])
async def get_subscribers(
    params: SubscribeSearchParams = Depends(),
    account_service: AccountService = Depends(get_account_service),
    # user_data: UserMiddleware = Depends(check_access),
):
    try:
        return await account_service.get_subscribers(params)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/subscriber-count", response_model=SubscribersCount)
async def get_subscriber_count(
    user: UserID = Depends(),
    account_service: AccountService = Depends(get_account_service),
    # user_data: UserMiddleware = Depends(check_access),
):
    try:
        return await account_service.get_subscribe_count(user)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
