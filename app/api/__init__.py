from fastapi import APIRouter
from app.api import admin 

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(admin.router)
