from app.api.routes.router import base_router as router
from app.database.session import sessionmanager
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.tables import create_tables
from starlette.middleware.sessions import SessionMiddleware
import os
import secrets

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

session_secrets = secrets.token_urlsafe(16)
app.add_middleware(SessionMiddleware, secret_key=session_secrets, max_age=3600, https_only=True)

