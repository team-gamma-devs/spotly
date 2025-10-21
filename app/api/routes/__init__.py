from fastapi import APIRouter
from app.api.routes import manager
from app.api.routes import signup
from app.api.routes import auth

api_router = APIRouter(prefix="/v1")

api_router.include_router(manager.router)
api_router.include_router(signup.router)
api_router.include_router(auth.router)
