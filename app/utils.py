from datetime import datetime, timedelta, timezone
import re
from typing import Annotated, Any, Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette import status

from app.config import ALGORITHM, SECRET_KEY
from app.dependencies import get_async_session
from app.models.queries import get_user_by_username
from app.models.schemas import ActiveUser, TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/accounts/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(
    username: str,
    password: str,
    async_session: async_sessionmaker[AsyncSession],
):
    user = await get_user_by_username(username, async_session)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    async_session: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session)
    ],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await get_user_by_username(
        username=token_data.username if token_data.username else "",
        async_session=async_session,
    )
    if user is None:
        raise credentials_exception
    return ActiveUser(**user.__dict__)


async def get_current_active_user(
    current_user: Annotated[ActiveUser, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


password_validation_exception = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Password can't be empty",
)


def compile_user_data(user_data: dict[str, Any]):
    if not user_data["password"]:
        raise password_validation_exception
    password_hash = get_password_hash(user_data["password"])
    user_data["password"] = password_hash
    return user_data
