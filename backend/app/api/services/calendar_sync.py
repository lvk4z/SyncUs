from datetime import datetime, timedelta, timezone
from typing import List
from app.core.google_client import get_calendar_service
from app.models.event import CalendarEventOutput

def fetch_google_events(refresh_token: str) -> List[CalendarEventOutput]:
    if not refresh_token:
        return []
    
    try:
        service = get_calendar_service(refresh_token)

        now = datetime.now(timezone.utc)
        time_min = (now - timedelta(days=1)).isoformat()
        time_max = (now + timedelta(days=7)).isoformat()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        items = events_result.get('items', [])
        formatted_events = []

        for item in items:
            start = item['start'].get('dateTime') or item['start'].get('date')
            end = item['end'].get('dateTime') or item['end'].get('date')

            formatted_events.append(CalendarEventOutput(
                id=item['id'],
                title=item.get('summary', '(Bez tytułu)'),
                start=start,
                end=end,
                source='google',
                color='#4285F4',
                description=item.get('description', '')
            ))

        return formatted_events
    
    except Exception as e:
        print(f"Events download failure {e}")
        return []
    