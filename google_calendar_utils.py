import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from collections import defaultdict
from config import GOOGLE_CLIENT_SECRET_FILE, GOOGLE_CALENDAR_SCOPES

EXCLUDED_MEETINGS = [
    'Isi Data Kehadiran CATAPA',
]

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', GOOGLE_CALENDAR_SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        except Exception as e:
            print("Token has expired or is invalid. Please log in again.")
            if os.path.exists('token.json'):
                os.remove('token.json')
            creds = None

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CLIENT_SECRET_FILE, GOOGLE_CALENDAR_SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def ordinal(n):
    return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

def format_time(dt):
    return dt.strftime('%-I:%M %p').lower().replace('am', 'AM').replace('pm', 'PM')

def format_time_range(start, end):
    return f"{format_time(start)} – {format_time(end)}"

def get_events_for_week():
    creds = get_credentials()
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        start_of_week = datetime.datetime.combine(start_of_week, datetime.time.min).isoformat() + 'Z'
        end_of_week = datetime.datetime.combine(end_of_week, datetime.time.max).isoformat() + 'Z'

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