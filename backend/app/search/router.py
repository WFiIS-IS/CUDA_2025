from fastapi import APIRouter

from app.db import DbSession
from app.schemas import SearchPublic

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/search", response_model=SearchPublic)
async def search(query: str, db: DbSession) -> SearchPublic:
    pass