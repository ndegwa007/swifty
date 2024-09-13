import os
import app.models as models
from passlib.context import CryptContext
from jose import JWTError, jwt 
from fastapi.security  import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.database.session import get_db_session
from sqlalchemy import select
from loguru import logger
from dotenv import load_dotenv 


load_dotenv()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



async  def get_user_by_username(username: str, db: AsyncSession = Depends(get_db_session)):
    user = (
        await db.scalars(select(models.User).where(models.User.username == username))
    ).first()
    return user

async def authenticate_user(username: str, password: str, db: AsyncSession = Depends(get_db_session)):
    user = await get_user_by_username(username, db)
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    return user



async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db_session)):
    logger.info(f"Received token: {token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        expiration = payload.get("exp")
        if username is None or expiration is None:
            logger.warning("Invalid payload in token")
            raise credentials_exception
        if datetime.now(timezone.utc) > datetime.fromtimestamp(expiration):
            logger.warning("Token has expired")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT decode error str({e})", exc_info=True)
        raise credentials_exception

    user = await get_user_by_username(username, db)
    if user is None:
        logger.warning(f"User not found: {username}")
        raise credentials_exception

    return user








