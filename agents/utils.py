import datetime
from config import REPO_OWNER, REPO_NAME
from date_time_utils import ordinal


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
    return [f"{pr['title']} [#{pr['number']}](https://github.com/{REPO_OWNER}/{REPO_NAME}/pull/{pr['number']})" for pr in reviewed_prs]

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