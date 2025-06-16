from fastapi import APIRouter

router = APIRouter(prefix="/search", tags=["search"])


# @router.get("/search", response_model=SearchPublic)
# async def search(query: str, db: DbSession) -> SearchPublic:
#     semantic_search = SemanticSearch(query)

#     result = await semantic_search.search()

#     return SearchPublic(results=result)
