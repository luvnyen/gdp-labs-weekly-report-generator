import datetime
from collections import defaultdict
from config import GOOGLE_CLIENT_SECRET_FILE, GOOGLE_CALENDAR_SCOPES, GOOGLE_MAIL_SCOPES, TIMEZONE
from googleapiclient.errors import HttpError
from google_api_utils import get_google_service
from date_time_utils import ordinal, format_time

EXCLUDED_MEETINGS = [
    'Isi Data Kehadiran CATAPA',
]

def format_time_range(start, end):
    return f"{format_time(start)} – {format_time(end)}"

def get_events_for_week():
    try:
        service = get_google_service('calendar', 'v3', 'token_calendar.json', GOOGLE_CALENDAR_SCOPES)
        
        today = datetime.datetime.now(TIMEZONE).date()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        start_of_week = datetime.datetime.combine(start_of_week, datetime.time.min, tzinfo=TIMEZONE).isoformat()
        end_of_week = datetime.datetime.combine(end_of_week, datetime.time.max, tzinfo=TIMEZONE).isoformat()

        events_result = service.events().list(calendarId='primary', timeMin=start_of_week,
                                              timeMax=end_of_week, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return []

        events_by_day = defaultdict(list)
        for event in events:
            summary = event['summary']
            if summary in EXCLUDED_MEETINGS:
                continue
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            start_dt = datetime.datetime.fromisoformat(start.rstrip('Z'))
            end_dt = datetime.datetime.fromisoformat(end.rstrip('Z'))
            day = start_dt.date()
            events_by_day[day].append((start_dt, end_dt, summary))

        formatted_events = []
        for day in sorted(events_by_day.keys()):
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