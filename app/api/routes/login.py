from fastapi import APIRouter, Depends, HTTPException, status
from app.Auth.auth  import ACCESS_TOKEN_EXPIRE, authenticate_user, get_current_user, create_access_token
from app.schemas import LoginCredentials, Token, User
from app.database.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta


router = APIRouter()


@router.post("/login/", response_model=Token)
async def login(credentials: LoginCredentials, db: AsyncSession = Depends(get_db_session)):
    user = await authenticate_user(credentials.username, credentials.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Incorrect username and password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expire)
    return {"access_token": access_token, "token_type": "Bearer"}


@router.get("/user/me/", response_model=User)
async def user_me(current_user: User =  Depends(get_current_user)):
    return current_user