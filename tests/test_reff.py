import pytest

from app.models.models import Users


def test_get_refferals(client):
    res = client.get("/api/refferal/id/1")
    assert res.status_code == 200
    assert len(res.json()["refferals"]) == 2

    fail_res_1 = client.get("/api/refferal/id/2")
    assert fail_res_1.status_code == 404


def test_get_code_by_email(client):
    res = client.get("/api/refferal/email/email1@gmail.com")
    assert res.status_code == 200
    assert res.json()["refferal_code"]

    res_fail = client.get("/api/refferal/email/email2@gmail.com")
    assert res_fail.json()["refferal_code"] is None


@pytest.mark.asyncio
async def test_register(client, async_session):
    json = {
        "username": "test",
        "email": "testemail@gmail.com",
        "password": "pass",
    }

    res = client.post("api/accounts/register", json=json)
    assert res.status_code == 201
    async with async_session() as session:
        user = await session.get(Users, 4)
        assert user

    fail_res = client.post("api/accounts/register", json=json)
    assert fail_res.status_code == 404


@pytest.mark.asyncio
async def test_register_with_ref(client, async_session):
    ref_code_res = client.get("/api/refferal/email/email1@gmail.com")
    ref_code = ref_code_res.json()["refferal_code"]
    json = {
        "username": "test5",
        "email": "testemail5@gmail.com",
        "password": "pass",
        "refferal_code": ref_code,
    }
    res = client.post("api/accounts/register", json=json)
    assert res.status_code == 201
    async with async_session() as session:
        new_user = await session.get(Users, 5)
        assert new_user
        head_user = await session.get(Users, 1)
        assert len(head_user.ref_users) == 3


def test_login(client):
    data = {
        "username": "username3",
        "password": "password",
        "email": "email@gmail.com",
    }
    res = client.post(
        "api/accounts/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert res.status_code == 200

    fail_data = {
        "username": "username3",
        "password": "password21312",
        "email": "email@gmail.com",
    }
    fail_res = client.post(
        "api/accounts/login",
        data=fail_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert fail_res.status_code == 401


@pytest.mark.asyncio
async def test_create_ref_code(client, async_session):
    data = {
        "username": "username3",
        "password": "password",
    }
    res_token = client.post(
        "api/accounts/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = res_token.json()["access_token"]

    async with async_session() as session:
        user = await session.get(Users, 3)
        assert user.refferal_code is None

    res = client.post(
        "api/refferal/create", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 201
    async with async_session() as session:
        user = await session.get(Users, 3)
        assert user.refferal_code


@pytest.mark.asyncio
async def test_delete_ref_code(client, async_session):
    data = {
        "username": "username3",
        "password": "password",
    }
    res_token = client.post(
        "api/accounts/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = res_token.json()["access_token"]

    async with async_session() as session:
        user = await session.get(Users, 3)
        assert user.refferal_code

    res = client.delete(
        "api/refferal/delete", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 201
    async with async_session() as session:
        user = await session.get(Users, 3)
        assert user.refferal_code is None
