from fastapi import APIRouter
from pydantic import BaseModel

from app.modules.scrapper.scrape_url_cli import process_url

router = APIRouter()


class ScrapperRequest(BaseModel):
    url: str


@router.post("/scrapper/")
async def scrapper(request: ScrapperRequest):
    results = await process_url(request.url)
    print(results)
    return {"result": "ok"}
