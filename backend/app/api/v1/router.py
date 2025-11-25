from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, pairs, google, slots

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(pairs.router, prefix="/pairs", tags=["pairs"])
api_router.include_router(google.router, prefix="/google", tags=["google"])
api_router.include_router(slots.router, prefix="/events", tags=["events"])
