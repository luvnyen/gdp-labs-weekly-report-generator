"""Google Forms Service Module

This module provides functionality to interact with Gmail API for retrieving
and formatting Google Forms submissions within the current week.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import cast, List, Dict, Any

from config.config import TIMEZONE
from core.services.google_service import get_google_service
from utils.date_time_util import ordinal, format_time

FORMS_RECEIPT_EMAIL = "forms-receipts-noreply@google.com"


def get_forms_filled_this_week() -> List[Dict[str, Any]]:
    """Retrieve Google Forms submissions from the current week.

    Fetches emails from Google Forms receipt address since the start of the
    current week and extracts form submission details.

    Returns:
        List[Dict[str, Any]]: List of form submissions with structure:
            {
                'title': str (form title),
                'timestamp': datetime (submission time in configured timezone)
            }
    """
    service = get_google_service('gmail', 'v1')

    today = datetime.now(TIMEZONE)
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    query = f"from:{FORMS_RECEIPT_EMAIL} after:{start_of_week.strftime('%Y/%m/%d')}"
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    filled_forms = []

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()

        email_data = msg['payload']['headers']
        subject = next(header['value'] for header in email_data if header['name'] == 'Subject')
        date_str = next(header['value'] for header in email_data if header['name'] == 'Date')

        timestamp = (cast(datetime, parsedate_to_datetime(date_str))
                     .astimezone(TIMEZONE)
                     .replace(second=0, microsecond=0))

        form_title = subject.replace("Response submitted:", "").strip()

        filled_forms.append({
            'title': form_title,
            'timestamp': timestamp
        })

    return filled_forms


def format_filled_forms(filled_forms: List[Dict[str, Any]]) -> List[str]:
    """Format form submissions into human-readable strings.

    Args:
        filled_forms (List[Dict[str, Any]]): List of form submissions from
            get_forms_filled_this_week()

    Returns:
        List[str]: Formatted strings with form title, submission date and time
            Example: "Daily Standup Form (submitted on Thursday, October 31st 2024 at 9:00 AM)"
    """
    formatted_forms = []
    for form in filled_forms:
        timestamp = form['timestamp']
        formatted_date = timestamp.strftime(f"%A, %B {ordinal(timestamp.day)}, %Y")
        formatted_time = format_time(timestamp)
        formatted_forms.append(f"{form['title']} (submitted on {formatted_date} at {formatted_time})")
    return formatted_forms


def get_this_week_filled_forms_formatted() -> List[str]:
    """Get a formatted list of forms submitted this week.

    Convenience function that combines retrieval and formatting of form submissions.

    Returns:
        List[str]: Formatted strings describing form submissions
    """
    filled_forms = get_forms_filled_this_week()
    return format_filled_forms(filled_forms)
