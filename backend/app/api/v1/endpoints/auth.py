import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import get_session
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.core.security import verify_password, create_access_token
from app.models.user import User

router = APIRouter()

@router.post("/login", response_model=dict)
async def login(
        userCredentials: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session)
):
    query = select(User).where(User.email == userCredentials.username)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist")
    
    if not verify_password(userCredentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Passwords incorrect")
    
    access_token = create_access_token(user.id)

    return {"access_token": access_token, "token_type": "bearer"}

    