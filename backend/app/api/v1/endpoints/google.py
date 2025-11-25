from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.db.engine import get_session
from app.core.security import get_current_user
from app.core.google_client import get_google_flow

router = APIRouter()

@router.get("/login")
async def google_login():
    flow = get_google_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return {"url": authorization_url}

@router.get("/callback")
async def google_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "No code found in url"}
    
    return {
        "message": "Copy this code and create a POST request to /connect endpoint",
        "code": code
    }

@router.post("/connect")
async def connect_google_account(
    code: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        flow = get_google_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials

        if not credentials.refresh_token:
            return {"warning": "No refresh_token returned. Did you revoke in accesGoogle settings"}
        
        current_user.google_token = credentials.refresh_token
        session.add(current_user)
        await session.commit()

        return {
            "status": "success",
            "msg": "Callendar connected"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
