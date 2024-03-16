from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.queries import startapp
from app.routers import account, refferal


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startapp(engine, Base)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(account.router)
app.include_router(refferal.router)
