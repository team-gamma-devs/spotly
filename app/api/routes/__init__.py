from fastapi import APIRouter
from app.api.routes import admin
from app.api.routes import signup

api_router = APIRouter(prefix="/v1")

api_router.include_router(admin.router)
api_router.include_router(signup.router)
