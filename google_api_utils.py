import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import GOOGLE_CLIENT_SECRET_FILE

def get_google_credentials(token_file, scopes):
    creds = None
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, scopes)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        except Exception as e:
            print(f"Token in {token_file} has expired or is invalid. Please log in again.")
            if os.path.exists(token_file):
                os.remove(token_file)
            creds = None

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CLIENT_SECRET_FILE, scopes)
        creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_google_service(api_name, api_version, token_file, scopes):
    creds = get_google_credentials(token_file, scopes)
    return build(api_name, api_version, credentials=creds)