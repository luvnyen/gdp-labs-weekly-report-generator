from datetime import datetime, timedelta
from google_api_utils import get_google_service
from config import GMAIL_SCOPES, TIMEZONE
from email.utils import parsedate_to_datetime
from date_time_utils import ordinal, format_time

FORMS_RECEIPT_EMAIL = "forms-receipts-noreply@google.com"

def get_forms_filled_this_week():
    service = get_google_service('gmail', 'v1', 'token.json', GMAIL_SCOPES)

    # Get the start of the week
    today = datetime.now(TIMEZONE)
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    # Search for emails from Google Forms
    query = f"from:{FORMS_RECEIPT_EMAIL} after:{start_of_week.strftime('%Y/%m/%d')}"
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    filled_forms = []

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        
        # Parse email content
        email_data = msg['payload']['headers']
        subject = next(header['value'] for header in email_data if header['name'] == 'Subject')
        date_str = next(header['value'] for header in email_data if header['name'] == 'Date')
        
        # Parse the date, convert to Jakarta time, and remove seconds
        timestamp = parsedate_to_datetime(date_str).astimezone(TIMEZONE).replace(second=0, microsecond=0)

        # Extract form title from subject
        form_title = subject.replace("Response submitted:", "").strip()

        filled_forms.append({
            'title': form_title,
            'timestamp': timestamp
        })

    return filled_forms

def format_filled_forms(filled_forms):
    formatted_forms = []
    for form in filled_forms:
        timestamp = form['timestamp']
        formatted_date = timestamp.strftime(f"%A, %B {ordinal(timestamp.day)}, %Y")
        formatted_time = format_time(timestamp)
        formatted_forms.append(f"{form['title']} (submitted on {formatted_date} at {formatted_time})")
    return formatted_forms

def get_this_week_filled_forms_formatted():
    filled_forms = get_forms_filled_this_week()
    return format_filled_forms(filled_forms)