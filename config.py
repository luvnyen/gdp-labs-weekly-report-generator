import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

load_dotenv(override=True)

def check_env_variables():
    required_vars = [
        'GITHUB_PERSONAL_ACCESS_TOKEN',
        'GITHUB_USERNAME',
        'GOOGLE_GEMINI_API_KEY',
        'GROQ_API_KEY',
        'REPO_NAME',
        'REPO_OWNER',
        'SONARQUBE_USER_TOKEN'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    # Check if GOOGLE_CLIENT_SECRET_FILE exists
    google_secret_file = os.getenv('GOOGLE_CLIENT_SECRET_FILE')
    if not google_secret_file or not os.path.isfile(google_secret_file):
        missing_vars.append('GOOGLE_CLIENT_SECRET_FILE (file not found)')
    
    if missing_vars:
        raise EnvironmentError(f"The following required environment variables are missing, empty, or invalid: {', '.join(missing_vars)}")

check_env_variables()

GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GOOGLE_CLIENT_SECRET_FILE = os.getenv('GOOGLE_CLIENT_SECRET_FILE')
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
REPO_NAME = os.getenv('REPO_NAME')
REPO_OWNER = os.getenv('REPO_OWNER')
SONARQUBE_USER_TOKEN = os.getenv('SONARQUBE_USER_TOKEN')

GMAIL_SEND_TO = os.getenv('GMAIL_SEND_TO')
GMAIL_SEND_CC = os.getenv('GMAIL_SEND_CC')
TIMEZONE = ZoneInfo("Asia/Jakarta")

GITHUB_API_BASE_URL = "https://api.github.com"

GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
GOOGLE_MAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

NAME_ON_REPORT = os.getenv('NAME_ON_REPORT')
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

SONARQUBE_API_URL = 'https://sqa.gdplabs.net/api/measures/component'
SONARQUBE_PROJECT = 'catapa-core'
SONARQUBE_PROJECT_DIRECTORY = 'src/main/java/com/catapa/core/personnel'
SONARQUBE_COMPONENT = f"{SONARQUBE_PROJECT}:src/main/java/com/catapa/core/personnel"
SONARQUBE_COMPONENT_URL = f"https://sqa.gdplabs.net/code?id={SONARQUBE_PROJECT}&selected={SONARQUBE_COMPONENT}"
