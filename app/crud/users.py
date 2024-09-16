from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import User, UserCreate, UserUpdate
import app.models as models
from typing import Sequence
from sqlalchemy import select
from fastapi import HTTPException
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError


async def create_user(db_session: AsyncSession, params: UserCreate) -> User:
    user = models.User(**params.model_dump())
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

async def get_users(db_session: AsyncSession) -> Sequence[User]:
    res = db_session.execute(select(models.User))
    users = res.scalars().all()
    return users


async def get_user(user_id: UUID, db_session: AsyncSession) -> User:
    user = (
        await db_session.scalars(select(models.User).where(models.User.userID == str(user_id)))
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found!")
    return user


async def update_user(user_id: UUID, params: UserUpdate, db_session: AsyncSession) -> User:
    from app.Auth.auth import get_password_hash # hashing the updated password 
    user = await get_user(user_id, db_session)

    for attr, value in params.model_dump(exclude_unset=True).items():
        
        if attr == 'password':
            value = get_password_hash(value)
        setattr(user, attr, value)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def delete_user(user_id: UUID, db_session: AsyncSession):
    user = await get_user(user_id, db_session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        await db_session.delete(user)
        await db_session.commit()
    except SQLAlchemyError as e:
        await db_session.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while deleting the user")

