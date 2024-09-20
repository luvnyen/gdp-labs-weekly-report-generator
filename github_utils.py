import requests
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from config import GITHUB_PERSONAL_ACCESS_TOKEN, REPO_OWNER, REPO_NAME, GITHUB_USERNAME, GITHUB_API_BASE_URL

# Define constants
PR_BASE_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/pull"
COMMIT_BASE_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/commit"

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
                        'sha': commit['sha'],
                        'message': commit['commit']['message'],
                        'date': commit['commit']['committer']['date'],
                    })
            url = response.links.get('next', {}).get('url')
        else:
            print(f"Error fetching commits for PR #{pr_number}: {response.status_code}")
            print(response.text)
            break

    return commits

def format_prs_and_commits(prs, pr_commits):
    formatted_output = []
    for pr in prs:
        pr_title = pr['title']
        pr_number = pr['number']
        pr_link = f"{PR_BASE_URL}/{pr_number}"
        
        formatted_pr = f"* {pr_title} [#{pr_number}]({pr_link})"
        formatted_output.append(formatted_pr)
        
        for commit in pr_commits[pr_number]:
            commit_sha = commit['sha'][:7]  # Short SHA
            commit_link = f"{COMMIT_BASE_URL}/{commit['sha']}"
            commit_message_lines = commit['message'].split('\n')
            commit_title = commit_message_lines[0]  # First line of commit message
            
            formatted_commit = f"   * [{commit_sha}]({commit_link}): {commit_title}"
            formatted_output.append(formatted_commit)
            
            # Add commit description bullets if they exist
            for line in commit_message_lines[1:]:
                stripped_line = line.strip()
                if stripped_line and (stripped_line.startswith('-') or stripped_line.startswith('*')):
                    formatted_output.append(f"      {stripped_line}")
        
        formatted_output.append("")  # Add an empty line between PRs
    
    return '\n'.join(formatted_output)

def get_pr_details(pr_number):
    url = f"{GITHUB_API_BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}"
    response = requests.get(url, headers=get_github_headers())
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching PR #{pr_number}: {response.status_code}")
        return None

def get_merged_prs_for_commit(commit_sha):
    url = f"{GITHUB_API_BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/commits/{commit_sha}/pulls"
    params = {"state": "closed"}
    response = requests.get(url, params=params, headers=get_github_headers())
    if response.status_code == 200:
        return [pr for pr in response.json() if pr['merged_at'] is not None and pr['user']['login'] == GITHUB_USERNAME]
    else:
        print(f"Error fetching PRs for commit {commit_sha}: {response.status_code}")
        return []

def get_merged_prs():
    start_of_week = get_start_of_week()
    start_of_week_str = start_of_week.strftime("%Y-%m-%d")

    query = f"repo:{REPO_OWNER}/{REPO_NAME} is:pr is:merged author:{GITHUB_USERNAME} merged:>={start_of_week_str} base:master base:main"
    url = f"{GITHUB_API_BASE_URL}/search/issues"
    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": 100
    }

    response = requests.get(url, params=params, headers=get_github_headers())
    if response.status_code == 200:
        merged_prs = response.json()['items']
        all_prs = []
        for pr in merged_prs:
            pr_details = get_pr_details(pr['number'])
            if pr_details:
                all_prs.append(pr_details)
                merge_commit_sha = pr_details['merge_commit_sha']
                nested_prs = get_merged_prs_for_commit(merge_commit_sha)
                all_prs.extend(nested_prs)
        return format_merged_prs(all_prs)
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
        reviewed_prs = response.json()['items']
        return format_prs(reviewed_prs)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []

def format_prs(prs):
    return [f"{pr['title']} [#{pr['number']}]({PR_BASE_URL}/{pr['number']})" for pr in prs]

def format_merged_prs(prs):
    formatted_prs = []
    for pr in prs:
        base_branch = pr['base']['ref']
        formatted_pr = f"{pr['title']} [#{pr['number']}]({PR_BASE_URL}/{pr['number']}) (merged into {base_branch})"
        formatted_prs.append(formatted_pr)
    return formatted_prs