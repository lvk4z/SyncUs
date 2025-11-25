from secrets import choice
from string import ascii_uppercase, digits
from typing import List
from unittest import result
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db.engine import get_session
from app.core.security import get_current_user
from sqlalchemy.orm import selectinload



from app.models.pair import Pair, PairCreate, PairRead
from app.models.user import User

router = APIRouter()

def _generate_code() -> str:
    chars = ascii_uppercase + digits
    first3 = ''.join(choice(chars) for _ in range(3))
    last3 = ''.join(choice(chars) for _ in range(3))
    return first3 + " " + last3

@router.post("/create", response_model=Pair)
async def create_pair(
    pair_in: PairCreate, 
    session: AsyncSession = Depends(get_session), 
    current_user: User = Depends(get_current_user)
    ) -> Pair:
    pair = Pair.model_validate(pair_in)
    code = _generate_code()
    query = select(Pair).where(Pair.code == code)
    result = await session.execute(query)
    if result.scalar_one_or_none():
        code = _generate_code()
    
    new_pair = Pair(
        name=pair.name,
        code=code,
        users=[current_user]
    )

    session.add(new_pair)
    await session.commit()
    await session.refresh(new_pair)

    return new_pair

@router.get("/my", response_model=List[PairRead])
async def get_my_pairs(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    query = select(User).where(User.id == current_user.id).options(selectinload(User.pairs))
    result = await session.execute(query)
    user_with_pairs = result.scalar_one()

    return user_with_pairs.pairs

@router.post("/join", response_model=Pair)
async def join_pair(
    code: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    query = select(Pair).where(Pair.code == code).options(selectinload(Pair.users))
    result = await session.execute(query)
    pair = result.scalar_one_or_none()

    if not pair:
        raise HTTPException(status_code=404, detail="Pair with that code does not exist")
    
    if any(u.id == current_user.id for u in pair.users):
        raise HTTPException(status_code=400, detail="User already joined this pair")
    
    pair.users.append(current_user)
    session.add(pair)
    await session.commit()
    await session.refresh(pair)

    return pair