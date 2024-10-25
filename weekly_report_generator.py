import datetime
from github_utils import GitHubService
from sonarqube_utils import get_test_coverage
from google_calendar_utils import get_events_for_week
from google_forms_utils import get_this_week_filled_forms_formatted
from llm_utils import summarize_accomplishments_with_llm
from config import SONARQUBE_COMPONENT_URL
from date_time_utils import ordinal
import user_input

def generate_weekly_report():
    current_date = datetime.datetime.now()
    current_month = current_date.strftime("%B")
    current_year = current_date.year

    is_h2 = current_date.month > 6
    half_year = "H2" if is_h2 else "H1"
    half_year_year = current_year if is_h2 else current_year

    # Initialize GitHub service
    github_service = GitHubService()

    # Fetch GitHub data from all repositories
    all_accomplishments = github_service.get_prs_and_commits()
    api_merged_prs = github_service.get_merged_prs()
    api_reviewed_prs = github_service.get_reviewed_prs()

    # Fetch SonarQube data
    test_coverage = get_test_coverage()

    # Fetch Google Calendar data
    all_meetings_and_activities = get_events_for_week()

    # Fetch Google Forms data using Gmail API
    google_forms_filled = get_this_week_filled_forms_formatted()

    # Write raw accomplishments to file
    with open('ACCOMPLISHMENTS_RAW.md', 'w') as f:
        f.write(all_accomplishments)
    
    # Use LLM to summarize accomplishments
    summarized_accomplishments = summarize_accomplishments_with_llm(all_accomplishments)

    # Generate the report using the template
    with open('TEMPLATE.md', 'r') as template_file:
        template = template_file.read()

    report_data = {
        'issues': format_list(user_input.issues, indent=""),
        'half_year': half_year,
        'half_year_year': half_year_year,
        'current_month': current_month,
        'current_year': current_year,
        'major_bugs_current_month': user_input.major_bugs_current_month,
        'minor_bugs_current_month': user_input.minor_bugs_current_month,
        'major_bugs_half_year': user_input.major_bugs_half_year,
        'minor_bugs_half_year': user_input.minor_bugs_half_year,
        'test_coverage': test_coverage,
        'sonarqube_component_url': SONARQUBE_COMPONENT_URL,
        'accomplishments': summarized_accomplishments,
        'deployments': format_list(api_merged_prs, indent="  "),
        'prs_reviewed': format_list(api_reviewed_prs, indent="  "),
        'meetings_and_activities': format_meetings(all_meetings_and_activities),
        'google_forms_filled': format_list(google_forms_filled, indent="  "),
        'wfo_days': format_wfo_days(user_input.wfo_days),
        'next_steps': format_list(user_input.next_steps, indent=""),
        'learning': format_list(user_input.learning, indent="")
    }

    report = template.format(**report_data)
    return report

def format_list(items, indent=""):
    if not items:
        return f"{indent}* None"
    return '\n'.join(f"{indent}* {item}" for item in items)

def format_meetings(meetings_and_activities):
    if not meetings_and_activities:
        return "  * None"
    return "\n".join(f"  {line}" for line in meetings_and_activities)

def format_wfo_days(days):
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    
    formatted_days = []
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    for day in days:
        if 1 <= day <= 5:
            date = monday + datetime.timedelta(days=day-1)
            formatted_days.append(f"{day_names[day-1]}, {date.strftime('%B')} {ordinal(date.day)}, {date.year}")
    
    return format_list(formatted_days, indent="  ")