import hashlib
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
from sqlmodel import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
PASSWORD_MAX_BYTES = 50

def _preprocess_password(password: str) -> str:
    """Pre-hash passwords that exceed the safe limit for bcrypt."""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > PASSWORD_MAX_BYTES:
        return hashlib.sha256(password_bytes).hexdigest()
    return password

def hash_pass(password: str) -> str:
    """Hash a password using bcrypt, with SHA256 pre-processing for long passwords."""
    processed = _preprocess_password(password)
    return pwd_context.hash(processed)

def create_access_token(subject: Union[str, Any]) -> str:
    """Create a JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "expire": expire.strftime("%Y-%m-%d %H:%M:%S"),
        "sub": str(subject)
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    processed = _preprocess_password(plain)
    return pwd_context.verify(processed, hashed_password)

async def get_current_user(
        token: Annotated[str, Depends(oauth_scheme)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> User:
    """Extract and validate the current user from JWT token."""
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
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