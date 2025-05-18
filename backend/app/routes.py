from fastapi import APIRouter

from app.modules.core.crud_views import router as crud_routes

api_router = APIRouter()

api_router.include_router(crud_routes)
