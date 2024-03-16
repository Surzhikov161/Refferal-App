import asyncio
from datetime import timedelta
import pytest
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from starlette.testclient import TestClient
from app.database.database import Base
from app.main import app
from app.dependencies import get_async_session
from app.models.models import RefferalCode, Users, refferals
from app.models.queries import startapp
from app.utils import create_access_token, get_password_hash

DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(DATABASE_URL, echo=True)
_async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


def override_get_async_session():
    return _async_session


app.dependency_overrides[get_async_session] = override_get_async_session


async def setUp():
    await startapp(engine, Base)

    users_to_insert = [
        {
            "id": 1,
            "username": "username1",
            "password": get_password_hash("password"),
            "email": "email1@gmail.com",
        },
        {
            "id": 2,
            "username": "username2",
            "password": get_password_hash("password"),
            "email": "email2@gmail.com",
        },
        {
            "id": 3,
            "username": "username3",
            "password": get_password_hash("password"),
            "email": "email3@gmail.com",
        },
    ]
    refferal_to_insert = [
        {"user_id": 1, "ref_id": 2},
        {"user_id": 1, "ref_id": 3},
    ]
    ref_code_token = create_access_token(
        {"email": "email1@gmail.com"}, timedelta(seconds=5)
    )
    async with _async_session() as session:
        async with session.begin():
            await session.run_sync(
                lambda session: session.bulk_insert_mappings(
                    Users, users_to_insert
                )
            )
            ref_code = RefferalCode(code=ref_code_token, user_id=1)
            session.add(ref_code)
            await session.execute(
                refferals.insert().values(),
                refferal_to_insert,
            )
            await session.commit()


asyncio.run(setUp())


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def async_session():
    return _async_session
