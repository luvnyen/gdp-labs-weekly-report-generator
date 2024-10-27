"""Google Service Module

This module provides core functionality for Google API authentication
and service initialization using OAuth 2.0 credentials.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config.config import GOOGLE_CLIENT_SECRET_FILE

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_google_credentials(token_file, scopes):
    # Construct an absolute path to a token file
    token_path = os.path.join(PROJECT_ROOT, 'tokens', token_file)

    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, scopes)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        except Exception:
            print(f"Token in {token_path} has expired or is invalid. Please log in again.")
            if os.path.exists(token_path):
                os.remove(token_path)
            creds = None

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CLIENT_SECRET_FILE, scopes)
        creds = flow.run_local_server(port=0)
        # Create tokens directory if it doesn't exist
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds

def get_google_service(api_name, api_version, token_file, scopes):
    creds = get_google_credentials(token_file, scopes)
    return build(api_name, api_version, credentials=creds)