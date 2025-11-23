from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import get_session
from app.models.user import User, UserCreate
from sqlmodel import select
from typing import List
from app.core.security import hash_pass

router = APIRouter()

@router.post("/create", response_model=User)
async def create_user(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    user = User.model_validate(user_in)
    hashed_password = hash_pass(user.password)
    user.password = hashed_password
    new_user = User(**user.model_dump())

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return new_user

@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    query = select(User).offset(skip).limit(limit)
    result = await session.execute(query)

    users = result.scalars().all()
    return users