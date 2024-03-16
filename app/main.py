from contextlib import asynccontextmanager
import time

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis


from app.database.database import Base, engine
from app.models.queries import create_meta
from app.routers import account, refferal


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_meta(engine, Base)
    redis = aioredis.from_url(
        "redis://localhost", encoding="utf8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(account.router)
app.include_router(refferal.router)


@app.get("/test")
@cache(expire=60)
async def asd():
    time.sleep(2)
    return {"12": "123"}
