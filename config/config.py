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
    """Enumeration of supported service types."""
    GITHUB = auto()
    SONARQUBE = auto()
    GOOGLE_CALENDAR = auto()
    GOOGLE_FORMS = auto()
    GMAIL = auto()
    LLM = auto()


class SonarQubeComponent(NamedTuple):
    """Represents a SonarQube component with project and path information.

    Attributes:
        project (str): Name of the SonarQube project
        path (str): Path within the project
    """
    project: str
    path: str

    @property
    def full_key(self) -> str:
        """Get the full component key in format 'project:path'.

        Returns:
            str: Full component key as 'project:path'
        """
        return f"{self.project}:{self.path}"

    @property
    def url(self) -> str:
        """Get the SonarQube URL for this component.

        Returns:
            str: Complete SonarQube URL for viewing this component
        """
        return f"https://sqa.gdplabs.net/code?id={self.project}&selected={self.project}:{self.path}"


@dataclass
class ServiceRequirements:
    """Class to define required environment variables for a service.

    Attributes:
        required_vars (Set[str]): Set of environment variable names required by the service
        alternative_vars (List[Set[str]]): List of alternative sets of variables, where any set being
                                         complete satisfies the requirement
    """
    required_vars: Set[str]
    alternative_vars: List[Set[str]] = None


class ConfigManager:
    """Manages configuration and environment variables for various services.

    This class handles loading, validation, and access to configuration settings
    for GitHub, Google APIs, SonarQube, and LLM services. It ensures required
    variables are present before allowing service access and supports alternative
    requirements for services that can use different providers.

    Attributes:
        env_vars (Dict[str, str]): Dictionary containing loaded environment variables
        _available_services (Set[ServiceType]): Set of services with satisfied requirements
        _service_requirements (Dict[ServiceType, ServiceRequirements]): Mapping of services
            to their configuration requirements
    """
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
        ServiceType.LLM: ServiceRequirements(
            required_vars = set(),
            alternative_vars = [
                {'GOOGLE_GEMINI_API_KEY'},
                {'GROQ_API_KEY'}
            ]
        )
    }

    def __init__(self):
        """Initialize ConfigManager by loading environment variables and checking service availability."""
        self.env_vars = self._load_env_vars()
        self._available_services: Set[ServiceType] = set()
        self._available_services = self._get_available_services()

    @staticmethod
    def _load_env_vars() -> Dict[str, str]:
        """Load environment variables into a dictionary.

        Returns:
            Dict[str, str]: Dictionary mapping environment variable names to their values
        """
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
        """Check if all required environment variables for a service are present.

        Validates that all required variables are set and any referenced files exist.
        For services with alternative requirements, checks if any set of alternatives is complete.

        Args:
            service_type (ServiceType): The service type to check requirements for

        Returns:
            bool: True if all required variables are present and valid, False otherwise
        """
        requirements = self._service_requirements[service_type]

        if not all(self.env_vars.get(var) for var in requirements.required_vars):
            return False

        if requirements.alternative_vars:
            alternatives_met = any(
                all(self.env_vars.get(var) for var in alt_set)
                for alt_set in requirements.alternative_vars
            )
            if not alternatives_met:
                return False

        if 'GOOGLE_CLIENT_SECRET_FILE' in requirements.required_vars:
            file_path = self.env_vars['GOOGLE_CLIENT_SECRET_FILE']
            if not os.path.isfile(file_path):
                return False

        return True

    def _get_available_services(self) -> Set[ServiceType]:
        """Get a set of services that have all their requirements satisfied.

        Returns:
            Set[ServiceType]: Set of available service types
        """
        available = set()
        for service_type in ServiceType:
            if self._check_service_requirements(service_type):
                available.add(service_type)
        return available

    def is_service_available(self, service_type: ServiceType) -> bool:
        """Check if a specific service is available.

        Args:
            service_type (ServiceType): Service type to check

        Returns:
            bool: True if service is available, False otherwise
        """
        return service_type in self._available_services

    def get_service_vars(self, service_type: ServiceType) -> Optional[Dict[str, str]]:
        """Get environment variables required for a specific service.

        Args:
            service_type (ServiceType): Service type to get variables for

        Returns:
            Optional[Dict[str, str]]: Dictionary of required variables if service is available,
                None otherwise
        """
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
        """Get GitHub personal access token.

        Returns:
            Optional[str]: GitHub token if available, None otherwise
        """
        return self.env_vars.get('GITHUB_PERSONAL_ACCESS_TOKEN')

    @property
    def github_username(self) -> Optional[str]:
        """Get GitHub username.

        Returns:
            Optional[str]: GitHub username if available, None otherwise
        """
        return self.env_vars.get('GITHUB_USERNAME')

    @property
    def github_repos(self) -> List[str]:
        """Get a list of GitHub repositories.

        Returns:
            List[str]: List of repository names, empty list if none configured
        """
        repos = self.env_vars.get('REPOS', '')
        if not repos:
            return []
        return [repo.strip() for repo in repos.split(',') if repo.strip()]

    @property
    def github_repo_owner(self) -> Optional[str]:
        """Get GitHub repository owner.

        Returns:
            Optional[str]: Repository owner if available, None otherwise
        """
        return self.env_vars.get('REPO_OWNER')

    @property
    def sonarqube_token(self) -> Optional[str]:
        """Get SonarQube user token.

        Returns:
            Optional[str]: SonarQube token if available, None otherwise
        """
        return self.env_vars.get('SONARQUBE_USER_TOKEN')

    @property
    def google_client_secret_file(self) -> Optional[str]:
        """Get a Google client secret file path.

        Returns:
            Optional[str]: Path to a client secret file if available, None otherwise
        """
        return self.env_vars.get('GOOGLE_CLIENT_SECRET_FILE')

    @property
    def gemini_api_key(self) -> Optional[str]:
        """Get Google Gemini API key.

        Returns:
            Optional[str]: Gemini API key if available, None otherwise
        """
        return self.env_vars.get('GOOGLE_GEMINI_API_KEY')

    @property
    def groq_api_key(self) -> Optional[str]:
        """Get Groq API key.

        Returns:
            Optional[str]: Groq API key if available, None otherwise
        """
        return self.env_vars.get('GROQ_API_KEY')

    @property
    def gmail_send_to(self) -> Optional[str]:
        """Get Gmail send-to address.

        Returns:
            Optional[str]: Email address if available, None otherwise
        """
        return self.env_vars.get('GMAIL_SEND_TO')

    @property
    def gmail_send_cc(self) -> Optional[str]:
        """Get Gmail CC address.

        Returns:
            Optional[str]: CC email address if available, None otherwise
        """
        return self.env_vars.get('GMAIL_SEND_CC')


def parse_sonarqube_components(components_str: str) -> List[SonarQubeComponent]:
    """Parse comma-separated SonarQube component string into component objects.

    Args:
        components_str (str): Comma-separated string of a project:path pairs

    Returns:
        List[SonarQubeComponent]: List of parsed SonarQubeComponent objects
    """
    if not components_str:
        return []

    components = []
    for component in components_str.split(','):
        component = unquote(component.strip())
        if ':' in component:
            project, path = component.split(':', 1)
            components.append(SonarQubeComponent(project.strip(), path.strip()))
    return components


config_manager = ConfigManager()

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
GOOGLE_GEMINI_API_KEY = config_manager.gemini_api_key
GROQ_API_KEY = config_manager.groq_api_key
GMAIL_SEND_TO = config_manager.gmail_send_to
GMAIL_SEND_CC = config_manager.gmail_send_cc
