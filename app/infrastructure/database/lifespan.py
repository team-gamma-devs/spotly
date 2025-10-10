from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.infrastructure.database import MongoDB
from app.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up mongo")
    await MongoDB.connect_db(
        mongodb_url=settings.mongodb_url, database_name=settings.mongodb_db_name
    )

    yield

    await MongoDB.close_db()
