from fastapi import APIRouter

from app.schemas.base import BaseSchema
from app.search.semantic import SemanticSearchDep

router = APIRouter(prefix="/search", tags=["search"])


class SearchPublic(BaseSchema):
    """Public model for search results."""

    results: list[str]


@router.get("/search", response_model=SearchPublic)
async def search(query: str, semantic_search: SemanticSearchDep) -> SearchPublic:
    result = await semantic_search.search(query)

    return SearchPublic(results=result)
