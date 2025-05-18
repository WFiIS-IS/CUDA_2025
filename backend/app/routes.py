from fastapi import APIRouter

from app.modules.core.crud_views import collection_routes

api_router = APIRouter()

api_router.include_router(
    collection_routes, prefix="/collections", tags=["collections"]
)
