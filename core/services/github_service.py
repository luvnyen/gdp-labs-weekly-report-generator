"""GitHub Service Module

This module provides functionality to interact with GitHub API for retrieving
and managing pull requests, commits, and reviewing activities.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import requests
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Tuple, Any
from config.config import GITHUB_PERSONAL_ACCESS_TOKEN, REPO_OWNER, REPOS, GITHUB_USERNAME, GITHUB_API_BASE_URL

class GitHubRepo:
    def __init__(self, name: str):
        self.name = name
        self.pr_base_url = f"https://github.com/{REPO_OWNER}/{name}/pull"
        self.commit_base_url = f"https://github.com/{REPO_OWNER}/{name}/commit"

    def get_pr_url(self, pr_number: int) -> str:
        return f"{self.pr_base_url}/{pr_number}"

    def get_commit_url(self, commit_sha: str) -> str:
        return f"{self.commit_base_url}/{commit_sha}"

def _get_start_of_week():
    today = datetime.now(timezone.utc).date()
    return today - timedelta(days=today.weekday())

def _format_prs_and_commits(repo: GitHubRepo, prs: List[Any], pr_commits: Dict[int, List[Any]]) -> str:
    formatted_output = []

    for pr in prs:
        pr_title = pr['title']
        pr_number = pr['number']
        pr_link = repo.get_pr_url(pr_number)

        formatted_pr = f"* {pr_title} [{repo.name}#{pr_number}]({pr_link})"
        formatted_output.append(formatted_pr)

        for commit in pr_commits[pr_number]:
            commit_sha = commit['sha'][:7]
            commit_link = repo.get_commit_url(commit['sha'])
            commit_message_lines = commit['message'].split('\n')
            commit_title = commit_message_lines[0]

            formatted_commit = f"   * [{commit_sha}]({commit_link}): {commit_title}"
            formatted_output.append(formatted_commit)

            # Add commit description bullets
            for line in commit_message_lines[1:]:
                stripped_line = line.strip()
                if stripped_line and (stripped_line.startswith('-') or stripped_line.startswith('*')):
                    formatted_output.append(f"      {stripped_line}")

        formatted_output.append("")  # Add empty line between PRs

    return '\n'.join(formatted_output) if formatted_output else ""

def _format_prs(repo: GitHubRepo, prs: List[Dict]) -> List[str]:
    return [
        f"{pr['title']} [{repo.name}#{pr['number']}]({repo.get_pr_url(pr['number'])})"
        for pr in prs
    ]

def _format_merged_prs(repo: GitHubRepo, prs: List[Dict]) -> List[str]:
    return [
        f"{pr['title']} [{repo.name}#{pr['number']}]({repo.get_pr_url(pr['number'])}) "
        f"(merged into {pr['base']['ref']})"
        for pr in prs
    ]

class GitHubService:
    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_PERSONAL_ACCESS_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.start_of_week = _get_start_of_week()
        self.start_of_week_datetime = datetime.combine(
            self.start_of_week, 
            datetime.min.time()
        ).replace(tzinfo=timezone.utc)

    def get_prs_and_commits(self) -> str:
        all_formatted_outputs = []
        
        for repo_name in REPOS:
            repo = GitHubRepo(repo_name)
            prs, pr_commits = self._fetch_repo_prs_and_commits(repo)
            formatted_output = _format_prs_and_commits(repo, prs, pr_commits)
            if formatted_output:
                all_formatted_outputs.append(formatted_output)
        
        return '\n'.join(all_formatted_outputs)

    def _fetch_repo_prs_and_commits(self, repo: GitHubRepo) -> Tuple[List[Any], Dict[int, List[Any]]]:
        url = f"{GITHUB_API_BASE_URL}/repos/{REPO_OWNER}/{repo.name}/pulls"
        params = {
            "state": "all",
            "sort": "updated",
            "direction": "desc",
            "per_page": 100
        }

        your_prs = []
        pr_commits = defaultdict(list)

        while url:
            response = requests.get(url, params=params, headers=self.headers)
            if response.status_code == 200:
                for pr in response.json():
                    pr_date = datetime.strptime(
                        pr['updated_at'], 
                        "%Y-%m-%dT%H:%M:%SZ"
                    ).replace(tzinfo=timezone.utc)
                    
                    if pr_date < self.start_of_week_datetime:
                        return your_prs, pr_commits
                    
                    if pr['user']['login'] == GITHUB_USERNAME:
                        # Get commits for this PR
                        commits = self._get_pr_commits(repo.name, pr['number'])
                        
                        # Only add PR if there are commits this week
                        if commits:
                            your_prs.append(pr)
                            pr_commits[pr['number']] = commits
                
                url = response.links.get('next', {}).get('url')
                params = {}
            else:
                print(f"Error fetching PRs for {repo.name}: {response.status_code}")
                print(response.text)
                break

        return your_prs, pr_commits

    def _get_pr_commits(self, repo_name: str, pr_number: int) -> List[Dict]:
        url = f"{GITHUB_API_BASE_URL}/repos/{REPO_OWNER}/{repo_name}/pulls/{pr_number}/commits"
        commits = []

        while url:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                for commit in response.json():
                    committer_date = datetime.strptime(
                        commit['commit']['committer']['date'],
                        "%Y-%m-%dT%H:%M:%SZ"
                    ).replace(tzinfo=timezone.utc)
                    
                    if (committer_date >= self.start_of_week_datetime and 
                        commit['author'] and 
                        commit['author']['login'] == GITHUB_USERNAME):
                        commits.append({
                            'sha': commit['sha'],
                            'message': commit['commit']['message'],
                            'date': commit['commit']['committer']['date'],
                        })
                url = response.links.get('next', {}).get('url')
            else:
                print(f"Error fetching commits for {repo_name} PR #{pr_number}: {response.status_code}")
                print(response.text)
                break

        return commits

    def get_merged_prs(self) -> List[str]:
        all_merged_prs = []
        
        for repo_name in REPOS:
            repo = GitHubRepo(repo_name)
            merged_prs = self._fetch_merged_prs(repo)
            all_merged_prs.extend(merged_prs)
        
        return all_merged_prs

    def _fetch_merged_prs(self, repo: GitHubRepo) -> List[str]:
        start_of_week_str = self.start_of_week.strftime("%Y-%m-%d")
        query = (
            f"repo:{REPO_OWNER}/{repo.name} is:pr is:merged "
            f"author:{GITHUB_USERNAME} merged:>={start_of_week_str} "
            f"base:master base:main"
        )
        
        url = f"{GITHUB_API_BASE_URL}/search/issues"
        params = {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": 100
        }

        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code == 200:
            merged_prs = response.json()['items']
            all_prs = []
            
            for pr in merged_prs:
                pr_details = self._get_pr_details(repo.name, pr['number'])
                if pr_details:
                    all_prs.append(pr_details)
                    merge_commit_sha = pr_details['merge_commit_sha']
                    nested_prs = self._get_merged_prs_for_commit(
                        repo.name,
                        merge_commit_sha
                    )
                    all_prs.extend(nested_prs)
            
            return _format_merged_prs(repo, all_prs)
        else:
            print(f"Error fetching merged PRs for {repo.name}: {response.status_code}")
            print(response.text)
            return []

    def _get_pr_details(self, repo_name: str, pr_number: int) -> Any | None:
        url = f"{GITHUB_API_BASE_URL}/repos/{REPO_OWNER}/{repo_name}/pulls/{pr_number}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching PR #{pr_number} for {repo_name}: {response.status_code}")
            return None

    def _get_merged_prs_for_commit(self, repo_name: str, commit_sha: str) -> List[Dict]:
        url = f"{GITHUB_API_BASE_URL}/repos/{REPO_OWNER}/{repo_name}/commits/{commit_sha}/pulls"
        params = {"state": "closed"}
        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code == 200:
            return [
                pr for pr in response.json() 
                if pr['merged_at'] is not None and pr['user']['login'] == GITHUB_USERNAME
            ]
        else:
            print(f"Error fetching PRs for commit {commit_sha} in {repo_name}: {response.status_code}")
            return []

    def get_reviewed_prs(self) -> List[str]:
        all_reviewed_prs = []
        
        for repo_name in REPOS:
            repo = GitHubRepo(repo_name)
            reviewed_prs = self._fetch_reviewed_prs(repo)
            all_reviewed_prs.extend(reviewed_prs)
        
        return all_reviewed_prs

    def _fetch_reviewed_prs(self, repo: GitHubRepo) -> List[str]:
        start_of_week_str = self.start_of_week.strftime("%Y-%m-%d")
        query = (
            f"repo:{REPO_OWNER}/{repo.name} is:pr "
            f"reviewed-by:{GITHUB_USERNAME} -author:{GITHUB_USERNAME} "
            f"updated:>={start_of_week_str}"
        )
        
        url = f"{GITHUB_API_BASE_URL}/search/issues"
        params = {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": 100
        }

        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code == 200:
            reviewed_prs = response.json()['items']
            return _format_prs(repo, reviewed_prs)
        else:
            print(f"Error fetching reviewed PRs for {repo.name}: {response.status_code}")
            print(response.text)
            return []

