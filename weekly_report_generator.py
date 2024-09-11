import datetime
from github_utils import get_prs_and_commits, get_merged_prs, get_reviewed_prs
from sonarqube_utils import get_test_coverage
from google_calendar_utils import get_events_for_week
from llm_utils import summarize_accomplishments_with_llm
import user_input

def generate_weekly_report():
    current_date = datetime.datetime.now()
    current_month = current_date.strftime("%B")
    current_year = current_date.year

    is_h2 = current_date.month > 6
    half_year = "H2" if is_h2 else "H1"
    half_year_year = current_year if is_h2 else current_year

    # Fetch GitHub data
    api_prs, api_pr_commits = get_prs_and_commits()
    api_merged_prs = get_merged_prs()
    api_reviewed_prs = get_reviewed_prs()

    # Fetch SonarQube data
    test_coverage = get_test_coverage()

    # Fetch Google Calendar data
    all_meetings_and_activities = get_events_for_week()

    # Prepare data for the report
    all_accomplishments = format_accomplishments(api_prs, api_pr_commits)
    
    # Write raw accomplishments to file
    with open('ACCOMPLISHMENTS_RAW.md', 'w') as f:
        f.write('\n'.join(all_accomplishments))
    
    all_deployments = format_deployments(api_merged_prs)
    all_prs_reviewed = format_reviewed_prs(api_reviewed_prs)

    # Use LLM to summarize accomplishments
    summarized_accomplishments = summarize_accomplishments_with_llm('\n'.join(all_accomplishments))

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
        'accomplishments': summarized_accomplishments,
        'deployments': format_list(all_deployments, indent="  "),
        'prs_reviewed': format_list(all_prs_reviewed, indent="  "),
        'meetings_and_activities': format_meetings(all_meetings_and_activities),
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

def format_accomplishments(prs, pr_commits):
    accomplishments = []
    for pr in prs:
        pr_number = pr['number']
        pr_title = pr['title']
        commits = pr_commits.get(pr_number, [])
        accomplishments.append(f"* PR #{pr_number} - {pr_title}")
        for commit in commits:
            message_lines = commit['message'].split('\n')
            accomplishments.append(f"   * Commit: {message_lines[0]}")  # First line (commit title)
            for line in message_lines[1:]:  # Remaining lines (description and bullet points)
                if line.strip():  # Only include non-empty lines
                    accomplishments.append(f"      {line.strip()}")
        accomplishments.append("")  # Add an empty line between PRs
    return accomplishments

def format_deployments(merged_prs):
    return [f"{pr['title']} #{pr['number']}" for pr in merged_prs]

def format_reviewed_prs(reviewed_prs):
    return [f"{pr['title']} [#{pr['number']}](https://github.com/GDP-ADMIN/CATAPA-API/pull/{pr['number']})" for pr in reviewed_prs]

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

def ordinal(n):
    return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

if __name__ == "__main__":
    report = generate_weekly_report()
    print(report)
