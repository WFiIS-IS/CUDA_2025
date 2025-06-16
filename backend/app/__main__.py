import asyncio
import logging

import uvicorn
from sqlmodel import select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.db import DbSessionManager, get_db_session_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init(session_manager: DbSessionManager) -> None:
    try:
        async with session_manager.get_session() as session:
            await session.execute(select(1))  # Simple query to check DB connection
    except Exception as e:
        logger.error(e)
        raise e


if __name__ == "__main__":

    async def main() -> None:
        logging.info("Waiting for DB to be ready...")
        session_manager = get_db_session_manager()
        await init(session_manager)
        logging.info("DB is ready, starting FastAPI app...")
        uvicorn.run("app.main:app", host="localhost", port=8080, reload=True)

    asyncio.run(main())
