from datetime import datetime
from weekly_report_generator import format_accomplishments, format_deployments, format_reviewed_prs, format_meetings, format_wfo_days
import user_input

def preprocess_data(collected_data):
    print("Preprocessing data...")
    current_date = datetime.now()
    current_month = current_date.strftime("%B")
    current_year = current_date.year
    is_h2 = current_date.month > 6
    half_year = "H2" if is_h2 else "H1"
    half_year_year = current_year if is_h2 else current_year

    return {
        'issues': format_list(user_input.issues, indent=""),
        'half_year': half_year,
        'half_year_year': half_year_year,
        'current_month': current_month,
        'current_year': current_year,
        'major_bugs_current_month': user_input.major_bugs_current_month,
        'minor_bugs_current_month': user_input.minor_bugs_current_month,
        'major_bugs_half_year': user_input.major_bugs_half_year,
        'minor_bugs_half_year': user_input.minor_bugs_half_year,
        'test_coverage': collected_data['sonarqube_coverage'],
        'accomplishments': format_accomplishments(collected_data['github_prs'], collected_data['github_commits']),
        'deployments': format_deployments(collected_data['github_merged_prs']),
        'prs_reviewed': format_reviewed_prs(collected_data['github_reviewed_prs']),
        'meetings_and_activities': format_meetings(collected_data['calendar_events']),
        'wfo_days': format_wfo_days(user_input.wfo_days),
        'next_steps': format_list(user_input.next_steps, indent=""),
        'learning': format_list(user_input.learning, indent="")
    }

def format_list(items, indent=""):
    if not items:
        return f"{indent}* None"
    return '\n'.join(f"{indent}* {item}" for item in items)