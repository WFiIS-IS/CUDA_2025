from fastapi import FastAPI

from app.config import settings
from app.routes import api_router

app = FastAPI(title=settings.PROJECT_NAME, root_path="/api")

app.include_router(api_router)
