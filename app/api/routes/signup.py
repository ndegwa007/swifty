from fastapi import APIRouter,  Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import User, UserCreate
from app.Auth.auth import get_user_by_username,  get_password_hash
from app.database.session import get_db_session
import app.crud.users as users


router = APIRouter()


@router.post("/signup",  response_model=User)
async def signup(user: UserCreate,  db: AsyncSession = Depends(get_db_session)):
    db_user  = await get_user_by_username(user.username, db)
    if db_user:
        raise HTTPException(status_code=400,detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    
    user_params = UserCreate(**user.model_dump())
    user_params.password = hashed_password
    new_user = await users.create_user(db, user_params)
    return new_user
