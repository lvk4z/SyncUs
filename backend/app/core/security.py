import select
from passlib.context import CryptContext
from datetime import timedelta, datetime
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from typing import Any, Union, Annotated
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from app.db.engine import get_session
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_pass(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any]) -> str:
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"expire": expire.strftime("%Y-%m-%d %H:%M:%S"), "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_password(plain: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain, hashed_password)

async def get_current_user(
        token: Annotated[str, Depends(oauth_scheme)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> User:
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload.get("sub")
        if user_id is None:
            raise exception
    except JWTError:
        raise exception
    
    result = await session.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise exception
    return user