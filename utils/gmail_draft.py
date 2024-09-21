from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from config import GOOGLE_MAIL_SCOPES, NAME_ON_REPORT
import base64

def get_date_range():
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=4)

    return f"{start_of_week.strftime('%B %d')}-{end_of_week.strftime('%d')}, {end_of_week.year}"

def create_gmail_draft(report, to, cc):
    creds = Credentials.from_authorized_user_file('token.json', GOOGLE_MAIL_SCOPES)
    
    service = build('gmail', 'v1', credentials=creds)

    date_range = get_date_range()
    
    # Please customize the message below as needed
    custom_message="""Dear Kak Sahat, AI Team, and BOSA Engineering Team,

Please find below the weekly report for the week of """+date_range+""".
    """

    message = MIMEText(f"""{custom_message}
                       """+report)
    message['to'] = to
    message['cc'] = cc
    message['subject'] = f'[Weekly Report: {NAME_ON_REPORT}] {date_range}'
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    draft = service.users().drafts().create(userId='me', body={
        'message': {
            'raw': raw_message
        }
    }).execute()
    
    print(f"Draft created with ID: {draft['id']}")
    return draft
