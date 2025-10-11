from fastapi import APIRouter
from app.api import admin
from app.api import signup

api_router = APIRouter(prefix="/v1")

api_router.include_router(admin.router)
api_router.include_router(signup.router)
