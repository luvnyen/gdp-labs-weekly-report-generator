
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

def create_gmail_draft(report, to, cc):
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.compose'])
    
    service = build('gmail', 'v1', credentials=creds)
    
    message = MIMEText(report)
    message['to'] = to
    message['cc'] = cc
    message['subject'] = 'Weekly Report'
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    draft = service.users().drafts().create(userId='me', body={
        'message': {
            'raw': raw_message
        }
    }).execute()
    
    print(f"Draft created with ID: {draft['id']}")
    return draft