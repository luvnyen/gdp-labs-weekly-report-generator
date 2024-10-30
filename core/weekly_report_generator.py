"""Weekly Report Generator Module

This module orchestrates the generation of weekly reports by collecting data from
various services including GitHub, SonarQube, Google Calendar, Google Forms, and Gmail.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
    - Glenn Steven Santoso (glenn.s.santoso@gdplabs.id)
"""
import datetime
import os
import time
from typing import Dict, List, Tuple

from config.config import ServiceType, config_manager
from core.services.github_service import GitHubService
from core.services.gmail_service import create_gmail_draft
from core.services.google_calendar_service import get_events_for_week
from core.services.google_forms_service import get_this_week_filled_forms_formatted
from core.services.llm_service import summarize_accomplishments_with_llm
from core.services.sonarqube_service import get_all_components_metrics, format_test_coverage_components
from .user_data import (
    ISSUES,
    MAJOR_BUGS_CURRENT_MONTH,
    MINOR_BUGS_CURRENT_MONTH,
    MAJOR_BUGS_HALF_YEAR,
    MINOR_BUGS_HALF_YEAR,
    WFO_DAYS,
    NEXT_STEPS,
    LEARNING,
    GMAIL_TEMPLATE
)


def update_progress(callback, task):
    if callback:
        callback(task)

def get_github_data(progress_callback) -> Dict[str, any]:
    if not config_manager.is_service_available(ServiceType.GITHUB):
        return {
            'accomplishments': "GitHub integration not configured",
            'deployments': [],
            'prs_reviewed': []
        }

    github_service = GitHubService()

    update_progress(progress_callback, "Fetching PRs and commits")
    accomplishments = github_service.get_prs_and_commits()

    if config_manager.is_service_available(ServiceType.LLM):
        update_progress(progress_callback, "Summarizing accomplishments with LLM")
        accomplishments = summarize_accomplishments_with_llm(accomplishments)

    update_progress(progress_callback, "Fetching merged PRs")
    deployments = github_service.get_merged_prs()

    update_progress(progress_callback, "Fetching reviewed PRs")
    prs_reviewed = github_service.get_reviewed_prs()

    return {
        'accomplishments': accomplishments,
        'deployments': deployments,
        'prs_reviewed': prs_reviewed
    }

def get_sonarqube_metrics(progress_callback) -> str:
    if not config_manager.is_service_available(ServiceType.SONARQUBE):
        return "SonarQube integration not configured"

    update_progress(progress_callback, "Fetching SonarQube metrics")
    metrics = get_all_components_metrics()
    return format_test_coverage_components(metrics)

def get_calendar_events(progress_callback) -> List[str]:
    if not config_manager.is_service_available(ServiceType.GOOGLE_CALENDAR):
        return ["Google Calendar integration not configured"]

    update_progress(progress_callback, "Fetching Google Calendar events")
    return get_events_for_week()

def get_forms_data(progress_callback) -> List[str]:
    if not config_manager.is_service_available(ServiceType.GOOGLE_FORMS):
        return ["Google Forms integration not configured"]

    update_progress(progress_callback, "Fetching Google Forms submissions")
    return get_this_week_filled_forms_formatted()

def generate_weekly_report(progress_callback=None) -> Tuple[str, float]:
    start_time = time.time()

    # Get current date info
    current_date = datetime.datetime.now()
    is_h2 = current_date.month > 6

    # Gather data from available services
    github_data = get_github_data(progress_callback)
    sonarqube_data = get_sonarqube_metrics(progress_callback)
    calendar_events = get_calendar_events(progress_callback)
    forms_data = get_forms_data(progress_callback)

    # Prepare report data
    report_data = {
        'issues': format_list(ISSUES),
        'half_year': "H2" if is_h2 else "H1",
        'half_year_year': current_date.year,
        'current_month': current_date.strftime("%B"),
        'current_year': current_date.year,
        'major_bugs_current_month': MAJOR_BUGS_CURRENT_MONTH,
        'minor_bugs_current_month': MINOR_BUGS_CURRENT_MONTH,
        'major_bugs_half_year': MAJOR_BUGS_HALF_YEAR,
        'minor_bugs_half_year': MINOR_BUGS_HALF_YEAR,
        'test_coverage_components': sonarqube_data,
        'accomplishments': github_data['accomplishments'],
        'deployments': format_list(github_data['deployments'], indent="  "),
        'prs_reviewed': format_list(github_data['prs_reviewed'], indent="  "),
        'meetings_and_activities': format_meetings(calendar_events),
        'google_forms_filled': format_list(forms_data, indent="  "),
        'wfo_days': format_wfo_days(WFO_DAYS),
        'next_steps': format_list(NEXT_STEPS),
        'learning': format_list(LEARNING)
    }

    # Generate a report from template
    template_path = os.path.join('templates', 'template.md')
    with open(template_path, 'r') as f:
        template = f.read()

    report = template.format(**report_data)

    # Create Gmail draft if available
    if config_manager.is_service_available(ServiceType.GMAIL):
        update_progress(progress_callback, "Creating Gmail draft")
        gmail_config = config_manager.get_service_vars(ServiceType.GMAIL)
        create_gmail_draft(
            report,
            gmail_config['GMAIL_SEND_TO'].split(','),
            gmail_config.get('GMAIL_SEND_CC', '').split(','),
            GMAIL_TEMPLATE
        )

    update_progress(progress_callback, None)
    return report, time.time() - start_time

def format_list(items: List[str], indent: str = "") -> str:
    if not items:
        return f"{indent}* None"
    return '\n'.join(f"{indent}* {item}" for item in items)

def format_meetings(meetings: List[str]) -> str:
    if not meetings:
        return "  * None"
    return "\n".join(f"  {line}" for line in meetings)

def format_wfo_days(days: List[int]) -> str:
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())

    formatted_days = []
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    for day in days:
        if 1 <= day <= 5:
            date = monday + datetime.timedelta(days=day - 1)
            formatted_days.append(
                f"{day_names[day - 1]}, {date.strftime('%B')} "
                f"{date.day}, {date.year}"
            )

    return format_list(formatted_days, indent="  ")