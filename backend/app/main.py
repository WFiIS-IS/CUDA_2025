from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.core.jobs import cleanup_orphaned_jobs
from app.routes import api_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    print("🚀 Starting FastAPI application...")
    await cleanup_orphaned_jobs()

    yield

    # Shutdown
    print("🔄 Shutting down FastAPI application...")


app = FastAPI(title=settings.PROJECT_NAME, root_path="/api", lifespan=lifespan)

app.include_router(api_router)
