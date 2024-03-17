from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette import status

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.dependencies import get_async_session
from app.models.queries import register_a_user
from app.models.schemas import ActiveUser, BaseUser, ReturnModel, Token
from app.utils import (
    authenticate_user,
    compile_user_data,
    create_access_token,
    get_current_active_user,
)

router = APIRouter(
    prefix="/api/accounts",
    tags=["accounts"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register/", response_model=ReturnModel)
async def register(
    user_data: BaseUser,
    request: Request,
    async_session: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session)
    ],
):
    user_data_compiled = compile_user_data(user_data.model_dump())
    res = await register_a_user(
        user_data=user_data_compiled,
        async_session=async_session,
    )
    if res:
        return JSONResponse(
            status_code=201,
            content={"result": True, "msg": "Success user registration"},
        )

    return JSONResponse(
        status_code=404,
        content={
            "result": False,
            "msg": (
                "Error during registration. Nickname or email is already taken"
            ),
        },
    )


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    async_session: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session)
    ],
) -> Token:
    user = await authenticate_user(
        form_data.username, form_data.password, async_session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
