"""Google Service Module with unified authentication.

This module provides core functionality for Google API authentication and service
initialization using a single OAuth 2.0 flow for all required scopes.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from config.config import GOOGLE_CLIENT_SECRET_FILE, GMAIL_SCOPES, GOOGLE_CALENDAR_SCOPES, GOOGLE_DOCS_SCOPES

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOKEN_FILE = 'google_token.json'
ALL_SCOPES = list(set(GMAIL_SCOPES + GOOGLE_CALENDAR_SCOPES + GOOGLE_DOCS_SCOPES))


def get_google_credentials() -> Credentials:
    """Get or refresh Google OAuth 2.0 credentials for all services.

    Uses a single token file and authentication flow for all required scopes.
    """
    token_path = os.path.join(PROJECT_ROOT, 'tokens', TOKEN_FILE)

    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, ALL_SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        except Exception:
            print(f"Token has expired or is invalid. Please log in again.")
            if os.path.exists(token_path):
                os.remove(token_path)
            creds = None

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CLIENT_SECRET_FILE, ALL_SCOPES)
        creds = flow.run_local_server(port=0)

        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_google_service(api_name: str, api_version: str) -> Resource:
    """Initialize a Google API service using shared credentials.

    Args:
        api_name: Name of the Google API service (e.g., 'gmail', 'calendar')
        api_version: API version to use (e.g., 'v1', 'v3')

    Returns:
        Resource: Authenticated Google API service instance
    """
    creds = get_google_credentials()
    return build(api_name, api_version, credentials=creds)
