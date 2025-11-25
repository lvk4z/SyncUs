from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import get_session
from app.models.user import User, UserCreate, UserRead
from sqlmodel import select
from typing import List
from app.core.security import hash_pass, get_current_user

router = APIRouter()

@router.post("/register", response_model=User)
async def create_user(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    query = select(User).where(User.email == user_in.email)
    result = await session.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email aleardy registered")
    
    user = User.model_validate(user_in)
    hashed_password = hash_pass(user.password)
    user.password = hashed_password
    new_user = User(**user.model_dump())

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return new_user

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return(current_user)

@router.get("/", response_model=List[UserRead])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    query = select(User).offset(skip).limit(limit)
    result = await session.execute(query)

    users = result.scalars().all()
    return users