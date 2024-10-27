"""Configuration Module

This module handles environment variables, configuration settings, and data structures
for various services including GitHub, Google APIs, SonarQube, and LLM services.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
    - Glenn Steven Santoso (glenn.s.santoso@gdplabs.id)
"""

import os
from urllib.parse import unquote
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from typing import List, NamedTuple

load_dotenv()

class SonarQubeComponent(NamedTuple):
    project: str
    path: str
    
    @property
    def full_key(self) -> str:
        return f"{self.project}:{self.path}"
    
    @property
    def url(self) -> str:
        return f"https://sqa.gdplabs.net/code?id={self.project}&selected={self.project}:{self.path}"

def parse_sonarqube_components(components_str: str) -> List[SonarQubeComponent]:
    if not components_str:
        return []
    
    components = []
    for component in components_str.split(','):
        component = unquote(component.strip())  # URL decode the component string
        if ':' in component:
            project, path = component.split(':', 1)
            components.append(SonarQubeComponent(project.strip(), path.strip()))
    return components

def check_env_variables():
    required_vars = [
        'AUTHOR_FULL_NAME',
        'GITHUB_PERSONAL_ACCESS_TOKEN',
        'GITHUB_USERNAME',
        'GOOGLE_GEMINI_API_KEY',
        'GROQ_API_KEY',
        'REPOS',
        'REPO_OWNER',
        'SONARQUBE_USER_TOKEN',
        'SONARQUBE_COMPONENTS',
        'GMAIL_SEND_TO',
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    # Check if GOOGLE_CLIENT_SECRET_FILE exists
    google_secret_file = os.getenv('GOOGLE_CLIENT_SECRET_FILE')
    if not google_secret_file or not os.path.isfile(google_secret_file):
        missing_vars.append('GOOGLE_CLIENT_SECRET_FILE (file not found)')
    
    if missing_vars:
        raise EnvironmentError(
            f"The following required environment variables are missing, empty, or invalid: {', '.join(missing_vars)}"
        )

check_env_variables()

AUTHOR_FULL_NAME = os.getenv('AUTHOR_FULL_NAME')
GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GOOGLE_CLIENT_SECRET_FILE = os.getenv('GOOGLE_CLIENT_SECRET_FILE')
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
REPOS: List[str] = os.getenv('REPOS', '').split(',')
REPO_OWNER = os.getenv('REPO_OWNER')
SONARQUBE_USER_TOKEN = os.getenv('SONARQUBE_USER_TOKEN')
SONARQUBE_COMPONENTS = parse_sonarqube_components(os.getenv('SONARQUBE_COMPONENTS', ''))
GMAIL_SEND_TO: List[str] = os.getenv('GMAIL_SEND_TO', '').split(',')
GMAIL_SEND_CC: List[str] = os.getenv('GMAIL_SEND_CC', '').split(',')

TIMEZONE = ZoneInfo("Asia/Jakarta")

GITHUB_API_BASE_URL = "https://api.github.com"

GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose'
]

SONARQUBE_API_URL = 'https://sqa.gdplabs.net/api/measures/component'