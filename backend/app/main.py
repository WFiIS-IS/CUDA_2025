from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.jobs import cleanup_orphaned_jobs
from app.routes import api_router
from app.settings import get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    print("🚀 Starting FastAPI application...")
    await cleanup_orphaned_jobs()

    yield

    # Shutdown
    print("🔄 Shutting down FastAPI application...")


settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME, root_path="/api", lifespan=lifespan)

app.include_router(api_router)
