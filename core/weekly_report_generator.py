# File: core/weekly_report_generator.py

import datetime
import os
import time
from core.services.github_service import GitHubService
from core.services.sonarqube_service import get_all_components_metrics, format_test_coverage_components
from core.services.google_calendar_service import get_events_for_week
from core.services.google_forms_service import get_this_week_filled_forms_formatted
from core.services.llm_service import summarize_accomplishments_with_llm
from utils.date_time_util import ordinal

# Get the project root directory (one level up from core)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Constants
ISSUES = []

MAJOR_BUGS_CURRENT_MONTH = 0
MINOR_BUGS_CURRENT_MONTH = 0

MAJOR_BUGS_HALF_YEAR = 0
MINOR_BUGS_HALF_YEAR = 0

WFO_DAYS = [1, 4, 5]

NEXT_STEPS = [
    "Adjust services for new employee and employee details (contact data, job experience, BPJS healthcare membership, employment data, identity card, family, and repository)",
]

LEARNING = [
    "[Head First Design Patterns, 2nd Edition](https://learning.oreilly.com/library/view/head-first-design/9781492077992/) by Eric Freeman & Elisabeth Robson (Chapter 3/13)",
    "[Introducing computer use, a new Claude 3.5 Sonnet, and Claude 3.5 Haiku](https://www.anthropic.com/news/3-5-models-and-computer-use)",
    "[Claude | Computer use for coding](https://youtu.be/vH2f7cjXjKI?si=eMYo2V0jXZLNkP9_)",
    "[Claude | Computer use for automating operations](https://youtu.be/ODaHJzOyVCQ?si=NGpUtA_dCTofYvU-)"
]

# Helper functions
def format_duration(seconds):
    """Format duration in seconds to a human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f} minutes"
    hours = minutes / 60
    return f"{hours:.1f} hours"

def format_list(items, indent=""):
    """Format a list of items with bullet points and optional indentation"""
    if not items:
        return f"{indent}* None"
    return '\n'.join(f"{indent}* {item}" for item in items)

def format_meetings(meetings_and_activities):
    """Format meetings and activities list"""
    if not meetings_and_activities:
        return "  * None"
    return "\n".join(f"  {line}" for line in meetings_and_activities)

def format_wfo_days(days):
    """Format work from office days into readable dates"""
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())

    formatted_days = []
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    for day in days:
        if 1 <= day <= 5:
            date = monday + datetime.timedelta(days=day - 1)
            formatted_days.append(f"{day_names[day - 1]}, {date.strftime('%B')} {ordinal(date.day)}, {date.year}")

    return format_list(formatted_days, indent="  ")

def generate_weekly_report(progress_callback=None):
    """Generate the weekly report with progress tracking"""
    overall_start_time = time.time()

    def update_progress(task):
        if progress_callback:
            progress_callback(task)

    # Get current date info
    current_date = datetime.datetime.now()
    current_month = current_date.strftime("%B")
    current_year = current_date.year

    is_h2 = current_date.month > 6
    half_year = "H2" if is_h2 else "H1"
    half_year_year = current_year if is_h2 else current_year

    # Fetching PRs and commits
    update_progress("Fetching PRs and commits")
    github_service = GitHubService()
    all_accomplishments = github_service.get_prs_and_commits()

    # Fetching merged PRs
    update_progress("Fetching merged PRs")
    api_merged_prs = github_service.get_merged_prs()

    # Fetching reviewed PRs
    update_progress("Fetching reviewed PRs")
    api_reviewed_prs = github_service.get_reviewed_prs()

    # SonarQube Data Collection
    update_progress("Fetching SonarQube metrics")
    sonarqube_metrics_list = get_all_components_metrics()

    # Google Calendar Data Collection
    update_progress("Fetching Google Calendar events")
    all_meetings_and_activities = get_events_for_week()

    # Google Forms Data Collection
    update_progress("Fetching Google Forms submissions")
    google_forms_filled = get_this_week_filled_forms_formatted()

    # Save raw accomplishments
    accomplishments_path = os.path.join(PROJECT_ROOT, 'ACCOMPLISHMENTS_RAW.md')
    with open(accomplishments_path, 'w') as f:
        f.write(all_accomplishments)

    # Summarize Accomplishments using LLM
    update_progress("Summarizing accomplishments with LLM")
    summarized_accomplishments = summarize_accomplishments_with_llm(all_accomplishments)

    # Generate Final Report
    update_progress("Generating final report")
    template_path = os.path.join(PROJECT_ROOT, 'templates', 'template.md')
    with open(template_path, 'r') as template_file:
        template = template_file.read()

    report_data = {
        'issues': format_list(ISSUES, indent=""),
        'half_year': half_year,
        'half_year_year': half_year_year,
        'current_month': current_month,
        'current_year': current_year,
        'major_bugs_current_month': MAJOR_BUGS_CURRENT_MONTH,
        'minor_bugs_current_month': MINOR_BUGS_CURRENT_MONTH,
        'major_bugs_half_year': MAJOR_BUGS_HALF_YEAR,
        'minor_bugs_half_year': MINOR_BUGS_HALF_YEAR,
        'test_coverage_components': format_test_coverage_components(sonarqube_metrics_list),
        'accomplishments': summarized_accomplishments,
        'deployments': format_list(api_merged_prs, indent="  "),
        'prs_reviewed': format_list(api_reviewed_prs, indent="  "),
        'meetings_and_activities': format_meetings(all_meetings_and_activities),
        'google_forms_filled': format_list(google_forms_filled, indent="  "),
        'wfo_days': format_wfo_days(WFO_DAYS),
        'next_steps': format_list(NEXT_STEPS, indent=""),
        'learning': format_list(LEARNING, indent="")
    }

    report = template.format(**report_data)

    # Update final progress
    update_progress(None)

    total_duration = time.time() - overall_start_time
    return report, total_duration