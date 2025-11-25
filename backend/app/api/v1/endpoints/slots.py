import asyncio
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.engine import get_session
from app.models.user import User
from app.models.event import Event, CalendarEventOutput
from app.core.security import get_current_user
from app.api.services.calendar_sync import fetch_google_events

router = APIRouter()

@router.get("/my-calendar", response_model=List[CalendarEventOutput])
async def get_my_calendar_events(
    session: AsyncSession = Depends(get_session),
    currnent_user: User = Depends(get_current_user)
):
    query = select(Event).where(Event.user_id == currnent_user.id)
    result = await session.execute(query)
    db_events = result.scalars().all()

    response_events = []
    for event in db_events:
        response_events.append(CalendarEventOutput(
            id=str(event.id), 
            title=event.title,
            start=event.start_time,
            end=event.end_time,
            source="manual",
            color="#34A853"  
        ))

    if currnent_user.google_token:
        google_events = await asyncio.to_thread(
            fetch_google_events,
            currnent_user.google_token
        )
        response_events.extend(google_events)

    response_events.sort(key=lambda x: str(x.start))

    return response_events