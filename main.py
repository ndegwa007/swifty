from app.api.routes.router import base_router as router
from app.database.session import sessionmanager
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.tables import create_tables
from app.config import settings
from starlette.middleware.sessions import SessionMiddleware
import os
import itsdangerous

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    handles startup and shutdown events
    """
    await create_tables()
    yield # important
    if sessionmanager.engine is not None:
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


app.add_middleware(SessionMiddleware, secret_key=os.getenv('JWT_SECRET_KEY'))

