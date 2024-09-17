import os
import app.models as models
from passlib.context import CryptContext
from jose import JWTError, jwt 
from fastapi.security  import OAuth2AuthorizationCodeBearer
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.database.session import get_db_session
from sqlalchemy import select
from loguru import logger
from dotenv import load_dotenv
import app.models as models

load_dotenv()

# OIDC CONFIGURATION
config = Config('.env')
oauth = OAuth(config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_id = os.getenv('GOOGLE_CLIENT_ID'),
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET'),
    client_kwargs={
        'scope': 'openid email profile',
    }
)



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 30

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)


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

"""
def decode_id_token(id_token):
    # Fetch Google public keys
    keys_url = 'https://www.googleapis.com/oauth2/v3/certs'
    keys = requests.get(keys_url).json()

    # Decode and verify token
    try:
        user_info = jwt.decode(id_token, keys, algorithms=['RS256'], audience=os.getenv('GOOGLE_CLIENT_ID'))
        return user_info
    except JWTError as e:
        logger.error(f"Failed to decode ID token: {e}")
        raise HTTPException(status_code=400, detail="Failed to decode ID token")
"""



async  def get_user_by_username(username: str, db: AsyncSession = Depends(get_db_session)):
    user = (
        await db.scalars(select(models.User).where(models.User.username == username))
    ).first()
    return user

async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db_session)):
    user = (await db.scalars(select(models.User).where(models.User.email == email))).first()
    return user



async def authenticate_user(username: str, password: str, db: AsyncSession = Depends(get_db_session)):
    user = await get_user_by_username(username, db)
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    return user



async def login(request: Request):
    redirect_uri = request.url_for('auth')
    state = os.getenv("SESSION_SECRET")
    request.session['oauth_state'] = state
    logger.info(f"Redirecting to Google with callback URL: {redirect_uri}")  
    response = await oauth.google.authorize_redirect(request, redirect_uri, state=state)
    logger.info(f"State sent: {request.session.get('oauth_state')}")
    return response
  

async def auth(request: Request, db: AsyncSession = Depends(get_db_session)):
    logger.info("Starting auth process")
    try:
        expected_state = request.session.pop('oauth_state', None)
        logger.info(f"expected_state: {expected_state}")

        received_state = request.query_params.get('state')
        logger.info(f"Received state from Google: {received_state}")

        token = await oauth.google.authorize_access_token(request)
                
        
        logger.info("Access token obtained from Google")
        logger.info(f"Token response: {token}")
        #id_token = token.get('id_token')
        # logger.info(f"id_token found: {id_token}")

        user_info = token.get('userinfo')  
        logger.info(f"ID token parsed. User info: {user_info}")
    except Exception as e:
        logger.error(f"Error during Google authentication: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to authenticate with Google")

    email = user_info.get('email')
    name = user_info.get('name')
    params = {"email": email, "username": name}

    if not email:
        logger.error("Email not provided by Google")
        raise HTTPException(status_code=400, detail="Email not provided by Google")

    user = await get_user_by_email(email, db)
    if not user:
        logger.info(f"Creating new user with email: {email}")
        user = models.User(email=email, username=name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        logger.info(f"User found with email: {email}")

    access_token = create_access_token({"sub": email, "name": name})
    logger.info(f"Access token created for user: {email}")
    return {"access_token": access_token, "token_type": "bearer", "user_info": user_info}


                            
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.error("Email not found in token")
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    logger.info(f"User authenticated: {email}")
    return {"email": email, "name": payload.get("name")}










