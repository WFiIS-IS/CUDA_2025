from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    root_path="/api",
    middleware=[Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])],
)

app.include_router(api_router)
