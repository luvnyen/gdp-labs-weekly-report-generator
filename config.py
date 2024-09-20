import os
from dotenv import load_dotenv

load_dotenv(override=True)

def check_env_variables():
    required_vars = [
        'GITHUB_PERSONAL_ACCESS_TOKEN',
        'GITHUB_USERNAME',
        'GOOGLE_CLIENT_SECRET_FILE',
        'GOOGLE_GEMINI_API_KEY',
        'GROQ_API_KEY',
        'REPO_NAME',
        'REPO_OWNER',
        'SONARQUBE_USER_TOKEN'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise EnvironmentError(f"The following required environment variables are missing or empty: {', '.join(missing_vars)}")

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

GITHUB_API_BASE_URL = "https://api.github.com"

GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

SONARQUBE_API_URL = 'https://sqa.gdplabs.net/api/measures/component'
SONARQUBE_COMPONENT = 'catapa-core:src/main/java/com/catapa/core/personnel'