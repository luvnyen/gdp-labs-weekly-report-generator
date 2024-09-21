from github_utils import get_prs_and_commits, get_merged_prs, get_reviewed_prs
from google_calendar_utils import get_events_for_week
from sonarqube_utils import get_test_coverage

def collect_all_data():
    print("Collecting data...")
    github_prs, github_commits = get_prs_and_commits()
    print("GitHub data collected.")
    github_merged_prs = get_merged_prs()
    print("GitHub merged PRs collected.")
    github_reviewed_prs = get_reviewed_prs()
    print("GitHub reviewed PRs collected.")
    calendar_events = get_events_for_week()
    print("Calendar events collected.")
    sonarqube_coverage = get_test_coverage()
    print("SonarQube data collected.")
    
    return {
        'github_prs': github_prs,
        'github_commits': github_commits,
        'github_merged_prs': github_merged_prs,
        'github_reviewed_prs': github_reviewed_prs,
        'calendar_events': calendar_events,
        'sonarqube_coverage': sonarqube_coverage
    }