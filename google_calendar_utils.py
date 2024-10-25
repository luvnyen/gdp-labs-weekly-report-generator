import datetime
from collections import defaultdict
from googleapiclient.errors import HttpError
from config import GOOGLE_CALENDAR_SCOPES, TIMEZONE
from google_api_utils import get_google_service
from date_time_utils import ordinal, format_time

EXCLUDED_MEETINGS = [
    'Isi Data Kehadiran CATAPA',
]

def format_time_range(start, end):
    return f"{format_time(start)} – {format_time(end)}"

def is_event_accepted_or_needs_action(event):
    """Check if the event is either accepted or has no response (needs action)"""
    # Get the list of attendees, defaulting to empty list if not present
    attendees = event.get('attendees', [])
    
    # Find the current user in the attendees list
    for attendee in attendees:
        # Check if this attendee is the current user (has 'self' field set to True)
        if attendee.get('self', False):
            # Return True if the response status is 'accepted' or 'needsAction'
            return attendee.get('responseStatus', 'needsAction') in ['accepted', 'needsAction']
    
    # If the event has no attendees or current user is not in attendees list
    # (e.g., events created by the user), consider it as accepted
    return True

def get_events_for_week():
    try:
        service = get_google_service('calendar', 'v3', 'token_calendar.json', GOOGLE_CALENDAR_SCOPES)
        
        today = datetime.datetime.now(TIMEZONE).date()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        start_of_week = datetime.datetime.combine(start_of_week, datetime.time.min, tzinfo=TIMEZONE).isoformat()
        end_of_week = datetime.datetime.combine(end_of_week, datetime.time.max, tzinfo=TIMEZONE).isoformat()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_of_week,
            timeMax=end_of_week,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            return []

        events_by_day = defaultdict(list)
        for event in events:
            # Skip excluded meetings and declined events
            if (event['summary'] in EXCLUDED_MEETINGS or
                not is_event_accepted_or_needs_action(event)):
                continue
                
            summary = event['summary']
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            start_dt = datetime.datetime.fromisoformat(start.rstrip('Z'))
            end_dt = datetime.datetime.fromisoformat(end.rstrip('Z'))
            day = start_dt.date()
            events_by_day[day].append((start_dt, end_dt, summary))

        formatted_events = []
        for day in sorted(events_by_day.keys()):
            # Only add days that have events after filtering
            if events_by_day[day]:
                day_str = day.strftime(f"%A, %B {ordinal(day.day)}, %Y")
                formatted_events.append(f"* **{day_str}**")
                for start, end, summary in events_by_day[day]:
                    time_range = format_time_range(start, end)
                    formatted_events.append(f"  * {time_range}: {summary}")

        # Remove any trailing empty strings
        while formatted_events and formatted_events[-1] == "":
            formatted_events.pop()

        return formatted_events

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []