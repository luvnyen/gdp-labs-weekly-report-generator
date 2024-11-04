"""GitHub Service Module

This module provides functionality to interact with GitHub API for retrieving
and managing pull requests, commits, and reviewing activities.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Any, Optional

import requests

from config.config import GITHUB_PERSONAL_ACCESS_TOKEN, REPO_OWNER, REPOS, GITHUB_USERNAME, GITHUB_API_BASE_URL


class GitHubRepo:
    """A class representing a GitHub repository with URL generation capabilities."""

    def __init__(self, name: str):
        """Initialize GitHubRepo with repository name."""
        self.name = name
        self.pr_base_url = f"https://github.com/{REPO_OWNER}/{name}/pull"
        self.commit_base_url = f"https://github.com/{REPO_OWNER}/{name}/commit"

    def get_pr_url(self, pr_number: int) -> str:
        """Generate URL for a specific pull request."""
        return f"{self.pr_base_url}/{pr_number}"

    def get_commit_url(self, commit_sha: str) -> str:
        """Generate URL for a specific commit."""
        return f"{self.commit_base_url}/{commit_sha}"


class GitHubService:
    """Service for interacting with GitHub API."""

    def __init__(self):
        """Initialize GitHubService with authentication headers and time settings."""
        self.headers = {
            "Authorization": f"token {GITHUB_PERSONAL_ACCESS_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.start_of_week = self._get_start_of_week()
        self.start_of_week_str = self.start_of_week.strftime("%Y-%m-%d")
        self.start_of_week_datetime = datetime.combine(
            self.start_of_week,
            datetime.min.time()
        ).replace(tzinfo=timezone.utc)

    def _get_start_of_week(self) -> datetime.date:
        """Get the date of the start of the current week (Monday)."""
        today = datetime.now(timezone.utc).date()
        return today - timedelta(days=today.weekday())

    def _get_pr_details(self, repo_name: str, pr_number: int) -> Optional[Dict]:
        """Get detailed information about a specific pull request."""
        url = f"{GITHUB_API_BASE_URL}/repos/{REPO_OWNER}/{repo_name}/pulls/{pr_number}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        print(f"Error fetching PR #{pr_number} for {repo_name}: {response.status_code}")
        return None

    def _get_pr_commits(self, repo_name: str, pr_number: int) -> List[Dict]:
        """Get commits from a specific pull request."""
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
                break

        return commits

    def _fetch_merged_prs(self, repo: GitHubRepo) -> List[str]:
        """Fetch merged pull requests from a repository."""
        query = (
            f"repo:{REPO_OWNER}/{repo.name} is:pr is:merged "
            f"author:{GITHUB_USERNAME} merged:>={self.start_of_week_str}"
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
            prs = []
            for item in response.json()['items']:
                pr_details = self._get_pr_details(repo.name, item['number'])
                if pr_details:
                    prs.append(pr_details)
            return self._format_merged_prs(repo, prs)

        print(f"Error fetching merged PRs for {repo.name}: {response.status_code}")
        return []

    def _format_merged_prs(self, repo: GitHubRepo, prs: List[Dict]) -> List[str]:
        """Format merged pull requests into strings.

        Format examples:
            feat(core): title CATAPA-API#123
            refactor(core): impl auto-approve for `ClassType` CATAPA-API#789
        """
        formatted_prs = []
        for pr in prs:
            title = pr['title']
            pr_number = pr['number']
            pr_link = repo.get_pr_url(pr_number)

            # Format without bullet point and without merged info
            formatted_pr = f"{title} [{repo.name}#{pr_number}]({pr_link})"
            formatted_prs.append(formatted_pr)

        return formatted_prs

    def _fetch_repo_prs_and_commits(self, repo: GitHubRepo) -> Tuple[List[Any], Dict[int, List[Any]]]:
        """Fetch PRs and their commits from a repository."""
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
                        commits = self._get_pr_commits(repo.name, pr['number'])
                        if commits:
                            your_prs.append(pr)
                            pr_commits[pr['number']] = commits

                url = response.links.get('next', {}).get('url')
                params = {}
            else:
                print(f"Error fetching PRs for {repo.name}: {response.status_code}")
                break

        return your_prs, pr_commits

    def _fetch_reviewed_prs(self, repo: GitHubRepo) -> List[str]:
        """Fetch reviewed pull requests from a repository."""
        query = (
            f"repo:{REPO_OWNER}/{repo.name} is:pr "
            f"reviewed-by:{GITHUB_USERNAME} -author:{GITHUB_USERNAME} "
            f"updated:>={self.start_of_week_str}"
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
            return [
                f"{pr['title']} [{repo.name}#{pr['number']}]({repo.get_pr_url(pr['number'])})"
                for pr in reviewed_prs
            ]

        print(f"Error fetching reviewed PRs for {repo.name}: {response.status_code}")
        return []

    def get_prs_and_commits(self) -> str:
        """Get formatted string of PRs and commits for all repositories."""
        all_formatted_outputs = []

        for repo_name in REPOS:
            repo = GitHubRepo(repo_name)
            prs, pr_commits = self._fetch_repo_prs_and_commits(repo)

            formatted_output = []
            for pr in prs:
                pr_title = pr['title']
                pr_number = pr['number']
                pr_link = repo.get_pr_url(pr_number)

                formatted_output.append(f"* {pr_title} [{repo.name}#{pr_number}]({pr_link})")

                for commit in pr_commits[pr_number]:
                    commit_sha = commit['sha'][:7]
                    commit_link = repo.get_commit_url(commit['sha'])
                    commit_message_lines = commit['message'].split('\n')
                    commit_title = commit_message_lines[0]

                    formatted_output.append(f"   * [{commit_sha}]({commit_link}): {commit_title}")

                    for line in commit_message_lines[1:]:
                        stripped_line = line.strip()
                        if stripped_line and (stripped_line.startswith('-') or stripped_line.startswith('*')):
                            formatted_output.append(f"      {stripped_line}")

                formatted_output.append("")

            if formatted_output:
                all_formatted_outputs.append('\n'.join(formatted_output))

        return '\n'.join(all_formatted_outputs)

    def get_merged_prs(self) -> List[str]:
        """Get a list of merged pull requests from all repositories."""
        all_merged_prs = []
        for repo_name in REPOS:
            repo = GitHubRepo(repo_name)
            merged_prs = self._fetch_merged_prs(repo)
            all_merged_prs.extend(merged_prs)
        return all_merged_prs

    def get_reviewed_prs(self) -> List[str]:
        """Get a list of pull requests reviewed across all repositories."""
        all_reviewed_prs = []
        for repo_name in REPOS:
            repo = GitHubRepo(repo_name)
            reviewed_prs = self._fetch_reviewed_prs(repo)
            all_reviewed_prs.extend(reviewed_prs)
        return all_reviewed_prs