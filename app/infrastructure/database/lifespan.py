from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.infrastructure.database import MongoDB
from app.settings import settings
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    This manages the lifecycle of the MongoDB connection:

    1. Connects to MongoDB before the application starts handling requests.
    2. Logs successful connection.
    3. Yields control to FastAPI to start serving requests.
    4. Logs any exceptions during connection and prevents app startup if connection fails.
    5. Closes MongoDB connection when the application shuts down, ensuring cleanup.

    Args:
        app (FastAPI): The FastAPI application instance.

    Raises:
        Exception: Re-raises any exception during MongoDB connection to stop the app startup.
    """
    try:
        logger.info("Starting connection to MongoDB...")
        await MongoDB.connect_db(
            mongodb_url=settings.mongodb_url, database_name=settings.mongodb_db_name
        )
        logger.info("MongoDB connected successfully")
        yield  # FastAPI starts accepting requests here
    except Exception as e:
        logger.exception("Failed to connect to MongoDB. App will not start.")
        raise e  # Prevent app startup if connection fails
    finally:
        logger.info("Closing MongoDB connection...")
        await MongoDB.close_db()
        logger.info("MongoDB connection closed")
