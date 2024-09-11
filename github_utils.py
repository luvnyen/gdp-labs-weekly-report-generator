import requests
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from config import GITHUB_PERSONAL_ACCESS_TOKEN, REPO_OWNER, REPO_NAME, GITHUB_USERNAME, GITHUB_API_BASE_URL

def get_github_headers():
    return {
        "Authorization": f"token {GITHUB_PERSONAL_ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def get_start_of_week():
    today = datetime.now(timezone.utc).date()
    return today - timedelta(days=today.weekday())

def get_prs_and_commits():
    start_of_week = get_start_of_week()
    start_of_week_datetime = datetime.combine(start_of_week, datetime.min.time()).replace(tzinfo=timezone.utc)
    
    url = f"{GITHUB_API_BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    params = {
        "state": "all",
        "sort": "updated",
        "direction": "desc",
        "per_page": 100
    }

    your_prs = []
    pr_commits = defaultdict(list)

    while url:
        response = requests.get(url, params=params, headers=get_github_headers())
        if response.status_code == 200:
            for pr in response.json():
                pr_date = datetime.strptime(pr['updated_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                if pr_date < start_of_week_datetime:
                    return your_prs, pr_commits
                if pr['user']['login'] == GITHUB_USERNAME:
                    your_prs.append(pr)
                    pr_commits[pr['number']] = get_pr_commits(pr['number'], start_of_week_datetime)
            url = response.links.get('next', {}).get('url')
            params = {}
        else:
            print(f"Error fetching PRs: {response.status_code}")
            print(response.text)
            break

    return your_prs, pr_commits

def get_pr_commits(pr_number, start_of_week):
    url = f"{GITHUB_API_BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/commits"
    commits = []

    while url:
        response = requests.get(url, headers=get_github_headers())
        if response.status_code == 200:
            for commit in response.json():
                committer_date = datetime.strptime(commit['commit']['committer']['date'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                if committer_date >= start_of_week and commit['author'] and commit['author']['login'] == GITHUB_USERNAME:
                    commits.append({
                        'message': commit['commit']['message'],
                        'date': commit['commit']['committer']['date'],
                    })
            url = response.links.get('next', {}).get('url')
        else:
            print(f"Error fetching commits for PR #{pr_number}: {response.status_code}")
            print(response.text)
            break

    return commits

def get_merged_prs():
    start_of_week = get_start_of_week()
    start_of_week_str = start_of_week.strftime("%Y-%m-%d")

    query = f"repo:{REPO_OWNER}/{REPO_NAME} is:pr is:merged author:{GITHUB_USERNAME} merged:>={start_of_week_str}"
    url = f"{GITHUB_API_BASE_URL}/search/issues"
    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": 100
    }

    response = requests.get(url, params=params, headers=get_github_headers())
    if response.status_code == 200:
        return response.json()['items']
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []

def get_reviewed_prs():
    start_of_week = get_start_of_week()
    start_of_week_str = start_of_week.strftime("%Y-%m-%d")

    query = f"repo:{REPO_OWNER}/{REPO_NAME} is:pr reviewed-by:{GITHUB_USERNAME} -author:{GITHUB_USERNAME} updated:>={start_of_week_str}"
    url = f"{GITHUB_API_BASE_URL}/search/issues"
    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": 100
    }

    response = requests.get(url, params=params, headers=get_github_headers())
    if response.status_code == 200:
        return response.json()['items']
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []