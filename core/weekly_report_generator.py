"""Weekly Report Generator Module

This module orchestrates the generation of weekly reports by collecting data from
various services including GitHub, SonarQube, Google Calendar, and Google Forms via Gmail.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
    - Glenn Steven Santoso (glenn.s.santoso@gdplabs.id)
"""

import datetime
import os
import time
from typing import Dict, List, Tuple, Callable, Optional, Any

from config.config import ServiceType, config_manager
from core.services.github_service import GitHubService
from core.services.google_calendar_service import get_events_for_week
from core.services.google_forms_service import get_this_week_filled_forms_formatted
from core.services.llm_service import summarize_with_gemini
from core.services.sonarqube_service import get_all_components_metrics, format_test_coverage_components
from utils.date_time_util import format_weekdays_with_dates, get_current_week_period, format_bulleted_list
from .user_data import (
    ISSUES, MAJOR_BUGS_CURRENT_MONTH, MINOR_BUGS_CURRENT_MONTH,
    MAJOR_BUGS_HALF_YEAR, MINOR_BUGS_HALF_YEAR, WFO_DAYS,
    OUT_OF_OFFICE_DAYS, NEXT_STEPS, LEARNING, OTHER_ACCOMPLISHMENTS, OMTM
)


def update_progress(callback: Optional[Callable[[str], None]], task: Optional[str]) -> None:
    """Update progress display with the current task.

    Args:
        callback: Function to call with task description
        task: Current task description
    """
    if callback:
        callback(task)


def get_github_data(progress_callback: Optional[Callable[[str], None]]) -> Dict[str, Any]:
    """Retrieve GitHub activity data including PRs and commits.

    Args:
        progress_callback: Function for progress updates

    Returns:
        Dict with keys:
            - accomplishments: Formatted PR and commit summary
            - deployments: List of merged PRs
            - prs_reviewed: List of reviewed PRs
    """
    if not config_manager.is_service_available(ServiceType.GITHUB):
        return {
            'accomplishments': "GitHub integration not configured",
            'deployments': [],
            'prs_reviewed': []
        }

    github_service = GitHubService()

    update_progress(progress_callback, "Fetching PRs and commits")
    accomplishments = github_service.get_prs_and_commits()

    with open('ACCOMPLISHMENTS_RAW.md', 'w') as f:
        f.write(accomplishments)

    if accomplishments and config_manager.is_service_available(ServiceType.LLM):
        update_progress(progress_callback, "Summarizing GitHub accomplishments with LLM")
        accomplishments = summarize_with_gemini(accomplishments)
        # accomplishments = summarize_with_groq(accomplishments)

    update_progress(progress_callback, "Fetching merged PRs")
    deployments = github_service.get_merged_prs()

    update_progress(progress_callback, "Fetching reviewed PRs")
    prs_reviewed = github_service.get_reviewed_prs()

    return {
        'accomplishments': accomplishments,
        'deployments': deployments,
        'prs_reviewed': prs_reviewed
    }


def get_sonarqube_metrics(progress_callback: Optional[Callable[[str], None]]) -> str:
    """Retrieve and format SonarQube test coverage metrics.

    Args:
        progress_callback: Function for progress updates

    Returns:
        Formatted test coverage report or error message
    """
    if not config_manager.is_service_available(ServiceType.SONARQUBE):
        return "SonarQube integration not configured"

    update_progress(progress_callback, "Fetching SonarQube metrics")
    metrics = get_all_components_metrics()
    return format_test_coverage_components(metrics)


def get_calendar_events(progress_callback: Optional[Callable[[str], None]]) -> List[str]:
    """Retrieve Google Calendar events for the week.

    Args:
        progress_callback: Function for progress updates

    Returns:
        List of formatted calendar events or error message
    """
    if not config_manager.is_service_available(ServiceType.GOOGLE_CALENDAR):
        return ["Google Calendar integration not configured"]

    update_progress(progress_callback, "Fetching Google Calendar events")
    return get_events_for_week()


def get_forms_data(progress_callback: Optional[Callable[[str], None]]) -> List[str]:
    """Retrieve Google Forms submissions for the week.

    Args:
        progress_callback: Function for progress updates

    Returns:
        List of formatted form submissions or error message
    """
    if not config_manager.is_service_available(ServiceType.GOOGLE_FORMS):
        return ["Google Forms integration not configured"]

    update_progress(progress_callback, "Fetching Google Forms submissions")
    return get_this_week_filled_forms_formatted()


def generate_weekly_report(
        progress_callback: Optional[Callable[[str], None]] = None
) -> Tuple[str, float]:
    """Generate a complete weekly report from all data sources.

    Args:
        progress_callback: Optional function for progress updates

    Returns:
        Tuple containing:
            - Generated report as Markdown string
            - Total generation time in seconds
    """
    start_time = time.time()

    current_date = datetime.datetime.now()
    is_h2 = current_date.month > 6

    github_data = get_github_data(progress_callback)
    sonarqube_data = get_sonarqube_metrics(progress_callback)
    calendar_events = get_calendar_events(progress_callback)
    forms_data = get_forms_data(progress_callback)

    report_data = {
        'period': get_current_week_period(),
        'issues': format_bulleted_list(ISSUES),
        'half_year': "H2" if is_h2 else "H1",
        'half_year_year': current_date.year,
        'current_month': current_date.strftime("%B"),
        'current_year': current_date.year,
        'major_bugs_current_month': MAJOR_BUGS_CURRENT_MONTH,
        'minor_bugs_current_month': MINOR_BUGS_CURRENT_MONTH,
        'major_bugs_half_year': MAJOR_BUGS_HALF_YEAR,
        'minor_bugs_half_year': MINOR_BUGS_HALF_YEAR,
        'test_coverage_components': sonarqube_data,
        'omtm': format_bulleted_list(OMTM),
        'github_accomplishments': github_data['accomplishments'],
        'other_accomplishments': format_bulleted_list(OTHER_ACCOMPLISHMENTS),
        'deployments': format_bulleted_list(github_data['deployments'], indent="  "),
        'prs_reviewed': format_bulleted_list(github_data['prs_reviewed'], indent="  "),
        'meetings_and_activities': format_meetings(calendar_events),
        'google_forms_filled': format_bulleted_list(forms_data, indent="  "),
        'wfo_days': format_weekdays_with_dates(WFO_DAYS),
        'out_of_office_days': format_weekdays_with_dates(OUT_OF_OFFICE_DAYS),
        'next_steps': format_bulleted_list(NEXT_STEPS),
        'learning': format_bulleted_list(LEARNING)
    }

    template_path = os.path.join('templates', 'template.md')
    with open(template_path, 'r') as f:
        template = f.read()

    report = template.format(**report_data)

    update_progress(progress_callback, None)
    return report, time.time() - start_time


def format_meetings(meetings: List[str]) -> str:
    """Format meeting list with consistent indentation.

    Args:
        meetings: List of meeting strings

    Returns:
        Formatted string with indented meetings
    """
    if not meetings:
        return "  * None"
    return "\n".join(f"  {line}" for line in meetings)
