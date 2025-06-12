from fastapi import APIRouter

from app.core.router import router as core_router
from app.scrapper.router import router as scrapper_router
from app.search.router import router as search_router

api_router = APIRouter()

api_router.include_router(core_router)
api_router.include_router(scrapper_router)
api_router.include_router(search_router)