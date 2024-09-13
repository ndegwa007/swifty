from fastapi import APIRouter, Depends
from app.schemas import User, UserCreate, UserUpdate
from typing import Sequence
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
import app.crud.users as users
from sqlalchemy import select
import app.models as models
from app.Auth.auth import get_password_hash
from uuid import UUID

router = APIRouter()

@router.post("/users/", response_model=User)
async def create_user(user: UserCreate,  db: AsyncSession = Depends(get_db_session)) -> User:
    logger.info(f"Creating user: {user}")
    user_params = UserCreate(**user.model_dump())
    user_params.password = get_password_hash(user.password)
    created_user = await users.create_user(db, user_params)
    logger.info(f"user_created: {created_user}")
    return created_user   

@router.get("/users/", response_model=list[User])
async def get_users(db: AsyncSession = Depends(get_db_session)) -> Sequence[User]:
    logger.info("fetching users")
    res  = await db.execute(select(models.User))
    users_list = res.scalars().all()
    logger.info(f"fetched users: {users_list}")
    return users_list


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db_session)) -> User:
    logger.info("fetch user")
    user = await users.get_user(user_id, db)
    logger.info(f"fetched user: {user}")
    return user


@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: UUID, params: UserUpdate, db: AsyncSession = Depends(get_db_session)) -> User:
    logger.info(f"updating user with id: {user_id}")
    user = await users.update_user(user_id, params, db)
    logger.info(f"updated user: {user}")
    return user


@router.delete("/users/{user_id}", response_model=User)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db_session)) -> User:
    logger.info(f"deleting user with id: {user_id}")
    user = await users.delete_user(user_id, db)
    logger.info(f"deleted user: {user}")
    return user




