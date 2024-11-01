"""Google Service Module

This module provides core functionality for Google API authentication
and service initialization using OAuth 2.0 credentials.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import os
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from config.config import GOOGLE_CLIENT_SECRET_FILE

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_google_credentials(token_file: str, scopes: List[str]) -> Credentials:
    """Get or refresh Google OAuth 2.0 credentials.

    Attempts to load credentials from an existing token file.
    If the token is expired, attempts to refresh it.
    If no valid token exists, initiates OAuth 2.0 flow to get new credentials.

    Args:
        token_file (str): Name of the token file to load/save credentials
        scopes (List[str]): List of required OAuth 2.0 scopes

    Returns:
        Credentials: Valid Google OAuth 2.0 credentials

    Notes:
        - Token files are stored in the 'tokens' directory under PROJECT_ROOT
        - Invalid tokens are automatically removed and regenerated
        - New tokens are obtained using local server OAuth flow
    """
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

        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_google_service(api_name: str, api_version: str, token_file: str, scopes: List[str]) -> Resource:
    """Initialize a Google API service with OAuth 2.0 authentication.

    Args:
        api_name (str): Name of the Google API service (e.g., 'gmail', 'calendar')
        api_version (str): API version to use (e.g., 'v1', 'v3')
        token_file (str): Name of the token file for credentials
        scopes (List[str]): List of required OAuth 2.0 scopes

    Returns:
        Resource: Authenticated Google API service instance
    """
    creds = get_google_credentials(token_file, scopes)
    return build(api_name, api_version, credentials=creds)
