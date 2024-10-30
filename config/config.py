"""Configuration Module

This module handles environment variables, configuration settings, and data structures
for various services including GitHub, Google APIs, SonarQube, and LLM services.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
    - Glenn Steven Santoso (glenn.s.santoso@gdplabs.id)
"""

import os
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, NamedTuple, Optional, Set
from urllib.parse import unquote
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

class ServiceType(Enum):
    GITHUB = auto()
    SONARQUBE = auto()
    GOOGLE_CALENDAR = auto()
    GOOGLE_FORMS = auto()
    GMAIL = auto()
    LLM = auto()

class SonarQubeComponent(NamedTuple):
    project: str
    path: str

    @property
    def full_key(self) -> str:
        return f"{self.project}:{self.path}"

    @property
    def url(self) -> str:
        return f"https://sqa.gdplabs.net/code?id={self.project}&selected={self.project}:{self.path}"

@dataclass
class ServiceRequirements:
    required_vars: Set[str]

class ConfigManager:
    _service_requirements = {
        ServiceType.GITHUB: ServiceRequirements({
            'GITHUB_PERSONAL_ACCESS_TOKEN',
            'GITHUB_USERNAME',
            'REPOS',
            'REPO_OWNER'
        }),
        ServiceType.SONARQUBE: ServiceRequirements({
            'SONARQUBE_USER_TOKEN',
            'SONARQUBE_COMPONENTS'
        }),
        ServiceType.GOOGLE_CALENDAR: ServiceRequirements({
            'GOOGLE_CLIENT_SECRET_FILE'
        }),
        ServiceType.GOOGLE_FORMS: ServiceRequirements({
            'GOOGLE_CLIENT_SECRET_FILE'
        }),
        ServiceType.GMAIL: ServiceRequirements({
            'GOOGLE_CLIENT_SECRET_FILE',
            'GMAIL_SEND_TO'
        }),
        ServiceType.LLM: ServiceRequirements({
            'GOOGLE_GEMINI_API_KEY',
            'GROQ_API_KEY'
        })
    }

    def __init__(self):
        self.env_vars = self._load_env_vars()
        self._available_services: Set[ServiceType] = set()
        self._available_services = self._get_available_services()

    def _load_env_vars(self) -> Dict[str, str]:
        return {
            'GITHUB_PERSONAL_ACCESS_TOKEN': os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN'),
            'GITHUB_USERNAME': os.getenv('GITHUB_USERNAME'),
            'GOOGLE_CLIENT_SECRET_FILE': os.getenv('GOOGLE_CLIENT_SECRET_FILE'),
            'GOOGLE_GEMINI_API_KEY': os.getenv('GOOGLE_GEMINI_API_KEY'),
            'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
            'REPOS': os.getenv('REPOS'),
            'REPO_OWNER': os.getenv('REPO_OWNER'),
            'SONARQUBE_USER_TOKEN': os.getenv('SONARQUBE_USER_TOKEN'),
            'SONARQUBE_COMPONENTS': os.getenv('SONARQUBE_COMPONENTS'),
            'GMAIL_SEND_TO': os.getenv('GMAIL_SEND_TO'),
            'GMAIL_SEND_CC': os.getenv('GMAIL_SEND_CC')
        }

    def _check_service_requirements(self, service_type: ServiceType) -> bool:
        requirements = self._service_requirements[service_type]

        if not all(self.env_vars.get(var) for var in requirements.required_vars):
            return False

        if 'GOOGLE_CLIENT_SECRET_FILE' in requirements.required_vars:
            file_path = self.env_vars['GOOGLE_CLIENT_SECRET_FILE']
            if not os.path.isfile(file_path):
                return False

        return True

    def _get_available_services(self) -> Set[ServiceType]:
        available = set()
        for service_type in ServiceType:
            if self._check_service_requirements(service_type):
                available.add(service_type)
        return available

    def is_service_available(self, service_type: ServiceType) -> bool:
        return service_type in self._available_services

    def get_service_vars(self, service_type: ServiceType) -> Optional[Dict[str, str]]:
        if not self.is_service_available(service_type):
            return None

        requirements = self._service_requirements[service_type]
        return {
            var: self.env_vars[var]
            for var in requirements.required_vars
            if var in self.env_vars
        }

    @property
    def github_token(self) -> Optional[str]:
        return self.env_vars.get('GITHUB_PERSONAL_ACCESS_TOKEN')

    @property
    def github_username(self) -> Optional[str]:
        return self.env_vars.get('GITHUB_USERNAME')

    @property
    def github_repos(self) -> List[str]:
        repos = self.env_vars.get('REPOS', '')
        if not repos:
            return []
        return [repo.strip() for repo in repos.split(',') if repo.strip()]

    @property
    def github_repo_owner(self) -> Optional[str]:
        return self.env_vars.get('REPO_OWNER')

    @property
    def sonarqube_token(self) -> Optional[str]:
        return self.env_vars.get('SONARQUBE_USER_TOKEN')

    @property
    def google_client_secret_file(self) -> Optional[str]:
        return self.env_vars.get('GOOGLE_CLIENT_SECRET_FILE')

    @property
    def groq_api_key(self) -> Optional[str]:
        return self.env_vars.get('GROQ_API_KEY')

    @property
    def gemini_api_key(self) -> Optional[str]:
        return self.env_vars.get('GOOGLE_GEMINI_API_KEY')

    @property
    def gmail_send_to(self) -> Optional[str]:
        return self.env_vars.get('GMAIL_SEND_TO')

    @property
    def gmail_send_cc(self) -> Optional[str]:
        return self.env_vars.get('GMAIL_SEND_CC')

def parse_sonarqube_components(components_str: str) -> List[SonarQubeComponent]:
    if not components_str:
        return []

    components = []
    for component in components_str.split(','):
        component = unquote(component.strip())
        if ':' in component:
            project, path = component.split(':', 1)
            components.append(SonarQubeComponent(project.strip(), path.strip()))
    return components

# Initialize global config manager
config_manager = ConfigManager()

# Constants
TIMEZONE = ZoneInfo("Asia/Jakarta")
GITHUB_API_BASE_URL = "https://api.github.com"
GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.compose']
SONARQUBE_API_URL = 'https://sqa.gdplabs.net/api/measures/component'

# Expose environment variables for backward compatibility
GITHUB_PERSONAL_ACCESS_TOKEN = config_manager.github_token
GITHUB_USERNAME = config_manager.github_username
REPOS = config_manager.github_repos
REPO_OWNER = config_manager.github_repo_owner
SONARQUBE_USER_TOKEN = config_manager.sonarqube_token
GOOGLE_CLIENT_SECRET_FILE = config_manager.google_client_secret_file
SONARQUBE_COMPONENTS = parse_sonarqube_components(config_manager.env_vars.get('SONARQUBE_COMPONENTS', ''))
GROQ_API_KEY = config_manager.groq_api_key
GOOGLE_GEMINI_API_KEY = config_manager.gemini_api_key
GMAIL_SEND_TO = config_manager.gmail_send_to
GMAIL_SEND_CC = config_manager.gmail_send_cc