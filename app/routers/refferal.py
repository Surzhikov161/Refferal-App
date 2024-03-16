from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.responses import JSONResponse

from app.dependencies import get_async_session
from app.models.queries import (
    add_refferal_code_to_user,
    delete_ref_code,
    get_refferal_code,
    get_user_by_username,
    get_user_refferals,
)
from app.models.schemas import (
    ActiveUser,
    ReturnModel,
    ReturnRefCode,
    ReturnRefferals,
)
from app.utils import create_access_token, get_current_active_user

router = APIRouter(
    prefix="/api/refferal",
    tags=["refferal"],
    responses={404: {"description": "Not found"}},
)


@router.get("/id/{id}", response_model=ReturnModel | ReturnRefferals)
async def get_refferals(
    id: int,
    async_session: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session)
    ],
):
    refferals = await get_user_refferals(id, async_session)
    if refferals is not None:
        return JSONResponse(
            status_code=200,
            content={
                "result": True,
                "refferals": [
                    {"id": ref.id, "username": ref.username}
                    for ref in refferals
                ],
            },
        )
    return JSONResponse(
        status_code=404,
        content={
            "result": False,
            "msg": "User not found or user doent't have a refferal code.",
        },
    )


@router.post("/create", response_model=ReturnModel | ReturnRefCode)
async def create_ref(
    current_user: Annotated[ActiveUser, Depends(get_current_active_user)],
    async_session: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session)
    ],
):
    user = await get_user_by_username(
        username=current_user.username,
        async_session=async_session,
    )
    access_token_expires = timedelta(minutes=30)
    ref_code_token = create_access_token(
        {"email": current_user.email}, access_token_expires
    )
    if not user.refferal_code:
        res = await add_refferal_code_to_user(
            user.id, ref_code_token, async_session
        )
        if res:
            return JSONResponse(
                status_code=201,
                content={
                    "refferal_code": ref_code_token,
                },
            )
        return JSONResponse(
            status_code=500,
            content={
                "result": False,
                "msg": "Server error",
            },
        )

    return JSONResponse(
        status_code=400,
        content={
            "result": False,
            "msg": "Ref code already exists",
        },
    )


@router.delete("/delete", response_model=ReturnModel)
async def delete_ref(
    current_user: Annotated[ActiveUser, Depends(get_current_active_user)],
    async_session: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session)
    ],
):
    user = await get_user_by_username(
        username=current_user.username,
        async_session=async_session,
    )
    if not user.refferal_code:
        return JSONResponse(
            status_code=400,
            content={"result": False, "msg": "User doesn't have a ref code."},
        )
    ref_code = user.refferal_code
    res = await delete_ref_code(ref_code, async_session)
    if res:
        return JSONResponse(
            status_code=201,
            content={
                "result": True,
                "msg": "Ref code succesfuly deleted",
            },
        )
    return JSONResponse(
        status_code=500,
        content={
            "result": False,
            "msg": "Server error",
        },
    )


@router.get("/email/{email}", response_model=ReturnRefCode)
async def get_ref_code_by_email(
    email: str,
    async_session: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session)
    ],
):
    refferal_code = await get_refferal_code(email, async_session)
    if refferal_code:
        return JSONResponse(
            status_code=200,
            content={"refferal_code": refferal_code},
        )
    return JSONResponse(
        status_code=404,
        content={
            "result": False,
            "msg": "User not found or user doesn't have refferal code",
        },
    )
