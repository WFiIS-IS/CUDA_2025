from fastapi import APIRouter

from app.modules.core.router import router as core_router
from app.modules.scrapper.router import router as scrapper_router

api_router = APIRouter()

api_router.include_router(core_router)
api_router.include_router(scrapper_router)
