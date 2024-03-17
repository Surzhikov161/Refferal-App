import time
from typing import Any, Optional

from fastapi import HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from jose import JWTError, jwt
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import noload
from starlette import status

from app.config import ALGORITHM, SECRET_KEY
from app.models.models import RefferalCode, Users, refferals


def raise_refferal_exception():
    refferal_validation_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Invalid refferal_code",
    )
    raise refferal_validation_exception


async def is_ref_valid(
    ref_code: str,
    async_session: async_sessionmaker[AsyncSession],
):
    try:
        payload = jwt.decode(ref_code, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email", "")
        user = await get_user_by_email(email, async_session)
        if user and user.refferal_code and user.refferal_code.code == ref_code:
            return user
        raise_refferal_exception()
    except JWTError:
        raise_refferal_exception()


async def get_user_by_username(
    username: str,
    async_session: async_sessionmaker[AsyncSession],
):
    async with async_session() as session:
        res = await session.execute(
            select(Users)
            .filter(Users.username.in_([username]))
            .options(noload(Users.ref_users))
        )
        await session.commit()
        user: Optional[Users] = res.scalars().one_or_none()
        return user


async def register_a_user(
    user_data: dict[str, Any],
    async_session: async_sessionmaker[AsyncSession],
):
    new_user = Users(
        username=user_data["username"],
        password=user_data["password"],
        email=user_data["email"],
    )
    if user_data["refferal_code"]:
        head_user = await is_ref_valid(
            user_data["refferal_code"], async_session
        )
        if head_user:
            return await add_user_and_ref(
                head_user=head_user,
                new_user=new_user,
                async_session=async_session,
            )
        return
    return await add_user(new_user, async_session)


async def add_user(
    user,
    async_session: async_sessionmaker[AsyncSession],
):
    try:
        async with async_session() as session:
            async with session.begin():
                session.add(user)
                await session.commit()
        return user
    except Exception:
        return


async def add_user_and_ref(
    head_user,
    new_user,
    async_session: async_sessionmaker[AsyncSession],
):
    try:
        async with async_session() as session:
            async with session.begin():
                session.add(new_user)
                await session.commit()
            statement = refferals.insert().values(
                user_id=head_user.id, ref_id=new_user.id
            )
            await session.execute(statement)
            await session.commit()
        return new_user
    except Exception:
        return


async def startapp(engine, Base):
    redis = aioredis.from_url(
        "redis://localhost", encoding="utf8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_refferal_code_to_user(
    user_id: int,
    code: str,
    async_session: async_sessionmaker[AsyncSession],
):
    try:
        async with async_session() as session:
            async with session.begin():
                ref_code = RefferalCode(code=code, user_id=user_id)
                session.add(ref_code)
                await session.commit()
        return True
    except Exception:
        return


async def delete_ref_code(
    ref_code: RefferalCode,
    async_session: async_sessionmaker[AsyncSession],
):
    try:
        async with async_session() as session:
            async with session.begin():
                await session.delete(ref_code)
                statement = refferals.delete().where(
                    refferals.c.user_id == ref_code.user_id,
                )
                await session.execute(statement)
                await session.commit()
        return True
    except Exception:
        return


async def get_user_by_email(
    email: str,
    async_session: async_sessionmaker[AsyncSession],
):
    async with async_session() as session:
        res = await session.execute(
            select(Users)
            .filter(Users.email.in_([email]))
            .options(noload(Users.ref_users))
        )
        await session.commit()
        user: Optional[Users] = res.scalars().one_or_none()
        if user:
            return user


@cache(expire=60)
async def get_refferal_code(
    email: str,
    async_session: async_sessionmaker[AsyncSession],
):
    async with async_session() as session:
        res = await session.execute(
            select(Users)
            .filter(Users.email.in_([email]))
            .options(noload(Users.ref_users))
        )
        await session.commit()
        user: Optional[Users] = res.scalars().one_or_none()
        if user and user.refferal_code:
            return user.refferal_code.code


async def get_user_refferals(
    id: int,
    async_session: async_sessionmaker[AsyncSession],
):
    async with async_session() as session:
        res = await session.execute(select(Users).filter(Users.id == id))
        await session.commit()
        user: Optional[Users] = res.unique().scalars().one_or_none()
        if user and user.refferal_code:
            return user.ref_users
