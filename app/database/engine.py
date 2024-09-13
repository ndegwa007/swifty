from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from app.config import settings
from loguru import logger

class EngineManager:
    _engine: AsyncEngine | None = None

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        if cls._engine is None:
            logger.info("Creating new database engine")
            cls._engine = create_async_engine(
                settings.database_url,
                echo=True,  # Set to False in production
                future=True,
            )
        return cls._engine

    @classmethod
    async def close_engine(cls):
        if cls._engine:
            logger.info("Closing database engine")
            await cls._engine.dispose()
            cls._engine = None

# Create a global instance of the engine
engine = EngineManager.get_engine()

# Function to get the engine (can be used in other parts of the application)
def get_engine() -> AsyncEngine:
    return EngineManager.get_engine()