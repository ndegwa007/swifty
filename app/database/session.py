from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    AsyncConnection,
    create_async_engine,
    async_sessionmaker
)
from fastapi import HTTPException
import contextlib
from app.config import settings
from typing import AsyncIterator
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from app.database.engine import get_engine

class DataSessionManager:
    # database session config
    def  __init__(self):
        self.engine: AsyncEngine = get_engine()
        self._sessionmaker:  async_sessionmaker[AsyncSession] = async_sessionmaker(autocommit=False, bind=self.engine)

    
    async def close(self):
        if self.engine is None:
            raise HTTPException(status_code=404, message="service unavailable!")
        await self.engine.dispose()
        self.engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connection(self) -> AsyncIterator[AsyncConnection]:
        if self.engine is None:
            raise HTTPException(status_code=404, message="Service not found!")
        
        async with self.engine.begin() as connection:
            try:
                yield connection
            except SQLAlchemyError:
                await connection.rollback()
                logger.error("Connection error occured")
                raise HTTPException(status_code=404)


    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            logger.error("sessionmaker is not available!")
            raise HTTPException(status_code=404)

        session = self._sessionmaker()

        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Session error could not be established {e}")
            raise HTTPException(status_code=404)


sessionmanager = DataSessionManager()


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session
