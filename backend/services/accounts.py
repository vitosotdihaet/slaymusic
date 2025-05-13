import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from dto.accounts import NewUser, User, UserID, NewRoleUser, UserUsername, LoginUserWithID
from repositories.interfaces import IUserRepository
from exceptions.accounts import (
    UserNotFoundException,
    InvalidCredentialsException,
    InvalidTokenException
)
from typing import Optional
from sqlalchemy.exc import IntegrityError
from exceptions.accounts import UserAlreadyExist

SECRET_KEY = os.getenv("SECRET_KEY", "insecure_default_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRED_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")


class AccountService:
    user_repository: IUserRepository

    def __init__(self, user_repository: IUserRepository) -> None:
        self.user_repository = user_repository

    async def create_user(self, new_user: NewRoleUser) -> User:
        hashed_password = self.get_hashed_password(new_user.password)
        user_with_hashed = new_user.model_copy(update={"password": hashed_password})
        user : User = None
        try:
            user = await self.user_repository.create_user(user_with_hashed)
        except IntegrityError as e:
            if 'users_username_key' in str(e.orig):
                raise UserAlreadyExist()
            raise e
        return user

    async def get_user(self, user_id: UserID) -> User:
        return await self.user_repository.get_user_by_id(user_id)
    
    async def get_user_by_username(self, username: UserUsername) -> LoginUserWithID:
        return await self.user_repository.get_user_by_username(username)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.user_repository.get_users(skip, limit)

    async def update_user(self, user: User) -> User:
        return await self.user_repository.update_user(user)

    async def delete_user(self, user_id: UserID) -> None:
        await self.user_repository.delete_user(user_id)

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRED_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    def verify_password(self, entered_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(entered_password, hashed_password)

    def get_hashed_password(self, entered_password: str) -> str:
        return pwd_context.hash(entered_password)

    async def get_user_from_token(self, token: str) -> User:
        payload = self.verify_token(token)
        if payload is None or "sub" not in payload:
            raise InvalidTokenException()

        try:
            user_id = UserID(id=payload["sub"])
        except Exception:
            raise InvalidTokenException()

        return await self.user_repository.get_user_by_id(user_id)

    
