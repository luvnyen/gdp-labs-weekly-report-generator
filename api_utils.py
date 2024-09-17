
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

def create_gmail_draft(report, to, cc):
    # Load credentials (you'll need to implement this based on your auth flow)
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

def create_google_sites_draft(report, site_id, page_name):
    # Load credentials (you'll need to implement this based on your auth flow)
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/sites'])
    
    service = build('sites', 'v1', credentials=creds)
    
    page = {
        'name': page_name,
        'content': {
            'type': 'docs',
            'docs': {
                'content': report
            }
        }
    }
    
    created_page = service.sites().pages().create(
        parent=f'sites/{site_id}',
        body=page
    ).execute()
    
    print(f"Draft page created with name: {created_page['name']}")
    return created_page