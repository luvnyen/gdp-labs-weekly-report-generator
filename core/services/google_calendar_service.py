"""Google Calendar Service Module

This module provides functionality to interact with Google Calendar API
for retrieving and formatting weekly events while handling event
acceptance statuses and time ranges.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import datetime
from collections import defaultdict
from typing import List, Dict, Any

from googleapiclient.errors import HttpError

from config.config import TIMEZONE
from core.services.google_service import get_google_service
from core.user_data import EXCLUDED_MEETINGS
from utils.date_time_util import ordinal, format_time


def format_time_range(start: datetime.datetime, end: datetime.datetime) -> str:
    """Format a time range in a consistent format.

    Args:
        start (datetime.datetime): Start time of the event
        end (datetime.datetime): End time of the event

    Returns:
        str: Formatted time range string (e.g., "9:00 AM – 10:00 AM")
    """
    return f"{format_time(start)} – {format_time(end)}"


def is_event_accepted_or_needs_action(event: Dict[str, Any]) -> bool:
    """Check if the event is either accepted or has no response.

    An event is considered valid if:
    - The user has accepted the invitation
    - The user hasn't responded yet (needs action)
    - The event has no attendees (e.g., personal events)
    - The user is not in the attendees list (e.g., events created by user)

    Args:
        event (Dict[str, Any]): Event data from Google Calendar API

    Returns:
        bool: True if event should be included based on acceptance status
    """
    attendees = event.get('attendees', [])

    for attendee in attendees:
        if attendee.get('self', False):
            return attendee.get('responseStatus', 'needsAction') in ['accepted', 'needsAction']

    return True


def get_events_for_week() -> List[str]:
    """Retrieve and format calendar events for the current week.

    Fetches events from Google Calendar API for the current week,
    filters based on acceptance status and exclusion list,
    and formats them in a Markdown list grouped by day.

    Events are sorted chronologically within each day.
    Days without events after filtering are omitted.

    Returns:
        List[str]: Markdown formatted list of events. Each day starts with a header
        followed by indented event entries with time and summary. Empty list if
        error occurs or no events found.

    Example output:
        [
            "* **Thursday, October 31st, 2024**",
            "* 9:00 AM – 10:00 AM: Team Meeting",
            "* 14:00 PM – 15:00 PM: Project Review"
        ]
    """
    try:
        service = get_google_service('calendar', 'v3')

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
            if event.get('eventType') == "workingLocation":
                continue

            if event['summary'] in EXCLUDED_MEETINGS or not is_event_accepted_or_needs_action(event):
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
            if events_by_day[day]:
                day_str = day.strftime(f"%A, %B {ordinal(day.day)}, %Y")
                formatted_events.append(f"* **{day_str}**")
                for start, end, summary in events_by_day[day]:
                    time_range = format_time_range(start, end)
                    formatted_events.append(f"  * {time_range}: {summary}")

        while formatted_events and formatted_events[-1] == "":
            formatted_events.pop()

        return formatted_events

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []
