from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.Auth.auth  import ACCESS_TOKEN_EXPIRE, authenticate_user, get_current_user, create_access_token, login, auth
from app.schemas import LoginCredentials, Token, User
from app.database.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from loguru import logger
from fastapi.responses import HTMLResponse


router = APIRouter()

"""
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
"""

@router.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <body>
            <h1>Welcome to the OpenID Connect Test</h1>
            <a href="/login">Login with Google</a>
        </body>
    </html>
    """

@router.get("/login")
async def login_route(request: Request):
    logger.info("Initiating login process")
    return await login(request)

@router.get("/auth", name="auth")
async def auth_route(request: Request, db: AsyncSession = Depends(get_db_session)):
    logger.info("Handling auth callback")
    try:
        result = await auth(request, db)
        logger.info(f"Auth successful. Access token created for user: {result['user_info']['email']}")
        return result
    except Exception as e:
        logger.error(f"Auth failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    logger.info(f"Protected route accessed by user: {current_user['email']}")
    return {"message": f"Hello, {current_user['name']}!"}