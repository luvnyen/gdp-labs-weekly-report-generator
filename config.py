import os
from dotenv import load_dotenv

load_dotenv()

def check_env_variables():
    required_vars = [
        'GITHUB_TOKEN',
        'GOOGLE_GEMINI_API_KEY',
        'GROQ_API_KEY',
        'SONARQUBE_USER_TOKEN',
        'GOOGLE_CLIENT_SECRET_FILE'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise EnvironmentError(f"The following required environment variables are missing or empty: {', '.join(missing_vars)}")

check_env_variables()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
SONARQUBE_USER_TOKEN = os.getenv('SONARQUBE_USER_TOKEN')
GOOGLE_CLIENT_SECRET_FILE = os.getenv('GOOGLE_CLIENT_SECRET_FILE')

REPO_OWNER = "GDP-ADMIN"
REPO_NAME = "CATAPA-API"
GITHUB_USERNAME = "GITHUB_USERNAME"

GITHUB_API_BASE_URL = "https://api.github.com"

SONARQUBE_API_URL = 'https://sqa.gdplabs.net/api/measures/component'
SONARQUBE_COMPONENT = 'catapa-core:src/main/java/com/catapa/core/personnel'