"""GitHub Service Module

This module provides functionality to interact with GitHub API for retrieving
and managing pull requests, commits, and reviewing activities.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Any

import requests

from config.config import GITHUB_PERSONAL_ACCESS_TOKEN, REPO_OWNER, REPOS, GITHUB_USERNAME, GITHUB_API_BASE_URL


class GitHubRepo:
    """Represents a GitHub repository with helper methods for URL generation.

    This class provides methods to generate URLs for pull requests and commits
    for a specific repository.

    Attributes:
        name (str): Repository name
        pr_base_url (str): Base URL for pull requests
        commit_base_url (str): Base URL for commits
    """

    def __init__(self, name: str):
        """Initialize GitHubRepo with repository name.

        Args:
            name (str): Name of the GitHub repository
        """
        self.name = name
        self.pr_base_url = f"https://github.com/{REPO_OWNER}/{name}/pull"
        self.commit_base_url = f"https://github.com/{REPO_OWNER}/{name}/commit"

    def get_pr_url(self, pr_number: int) -> str:
        """Generate URL for a specific pull request.

        Args:
            pr_number (int): Pull request number

        Returns:
            str: Complete URL to the pull request
        """
        return f"{self.pr_base_url}/{pr_number}"

    def get_commit_url(self, commit_sha: str) -> str:
        """Generate URL for a specific commit.

        Args:
            commit_sha (str): Commit SHA hash

        Returns:
            str: Complete URL to the commit
        """
        return f"{self.commit_base_url}/{commit_sha}"


def _get_start_of_week() -> datetime.date:
    """Get the date of the start of the current week (Monday).

    Returns:
        datetime.date: Date of the current week's Monday
    """
    today = datetime.now(timezone.utc).date()
    return today - timedelta(days=today.weekday())


def _format_prs_and_commits(repo: GitHubRepo, prs: List[Any], pr_commits: Dict[int, List[Any]]) -> str:
    """Format pull requests and their commits into a Markdown string.

    Args:
        repo (GitHubRepo): Repository object
        prs (List[Any]): List of pull request data
        pr_commits (Dict[int, List[Any]]): Dictionary mapping PR numbers to their commits

    Returns:
        str: Formatted Markdown string containing PR and commit information
    """
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

            for line in commit_message_lines[1:]:
                stripped_line = line.strip()
                if stripped_line and (stripped_line.startswith('-') or stripped_line.startswith('*')):
                    formatted_output.append(f"      {stripped_line}")

        formatted_output.append("")

    return '\n'.join(formatted_output) if formatted_output else ""


def _format_prs(repo: GitHubRepo, prs: List[Dict]) -> List[str]:
    """Format pull requests into a list of Markdown strings.

    Args:
        repo (GitHubRepo): Repository object
        prs (List[Dict]): List of pull request data

    Returns:
        List[str]: List of formatted PR strings in Markdown format
    """
    return [
        f"{pr['title']} [{repo.name}#{pr['number']}]({repo.get_pr_url(pr['number'])})"
        for pr in prs
    ]


def _format_merged_prs(repo: GitHubRepo, prs: List[Dict]) -> List[str]:
    """Format merged pull requests into a list of Markdown strings.

    Args:
        repo (GitHubRepo): Repository object
        prs (List[Dict]): List of merged pull request data

    Returns:
        List[str]: List of formatted merged PR strings in Markdown format
    """
    return [
        f"{pr['title']} [{repo.name}#{pr['number']}]({repo.get_pr_url(pr['number'])}) "
        f"(merged into {pr['base']['ref']})"
        for pr in prs
    ]


class GitHubService:
    """Service for interacting with GitHub API.

    This class provides methods to fetch and process pull requests, commits,
    and reviewing activities from GitHub repositories.

    Attributes:
        headers (Dict[str, str]): HTTP headers for GitHub API requests
        start_of_week (datetime.date): Date of the current week's Monday
        start_of_week_datetime (datetime): Start of week as datetime with UTC timezone
    """

    def __init__(self):
        """Initialize GitHubService with authentication headers and time settings."""
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
        """Get formatted string of PRs and commits for all repositories.

        Returns:
            str: Markdown formatted string containing all PRs and their commits
        """
        all_formatted_outputs = []

        for repo_name in REPOS:
            repo = GitHubRepo(repo_name)
            prs, pr_commits = self._fetch_repo_prs_and_commits(repo)
            formatted_output = _format_prs_and_commits(repo, prs, pr_commits)
            if formatted_output:
                all_formatted_outputs.append(formatted_output)

        return '\n'.join(all_formatted_outputs)

    def _fetch_repo_prs_and_commits(self, repo: GitHubRepo) -> Tuple[List[Any], Dict[int, List[Any]]]:
        """Fetch PRs and their commits from a repository.

        Args:
            repo (GitHubRepo): Repository to fetch from

        Returns:
            Tuple[List[Any], Dict[int, List[Any]]]: Tuple containing list of PRs and
                dictionary mapping PR numbers to their commits
        """
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
                print(response.text)
                break

        return your_prs, pr_commits

    def _get_pr_commits(self, repo_name: str, pr_number: int) -> List[Dict]:
        """Get commits from a specific pull request.

        Args:
            repo_name (str): Repository name
            pr_number (int): Pull request number

        Returns:
            List[Dict]: List of commit data dictionaries
        """
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
        """Get a list of merged pull requests from all repositories.

        Returns:
            List[str]: List of formatted strings describing merged PRs
        """
        all_merged_prs = []

        for repo_name in REPOS:
            repo = GitHubRepo(repo_name)
            merged_prs = self._fetch_merged_prs(repo)
            all_merged_prs.extend(merged_prs)

        return all_merged_prs

    def _fetch_merged_prs(self, repo: GitHubRepo) -> List[str]:
        """Fetch merged pull requests from a repository.

        Args:
            repo (GitHubRepo): Repository to fetch from

        Returns:
            List[str]: List of formatted strings describing merged PRs
        """
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
        """Get detailed information about a specific pull request.

        Args:
            repo_name (str): Repository name
            pr_number (int): Pull request number

        Returns:
            Any | None: Pull request details if successful, None otherwise
        """
        url = f"{GITHUB_API_BASE_URL}/repos/{REPO_OWNER}/{repo_name}/pulls/{pr_number}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching PR #{pr_number} for {repo_name}: {response.status_code}")
            return None

    def _get_merged_prs_for_commit(self, repo_name: str, commit_sha: str) -> List[Dict]:
        """Get merged pull requests associated with a specific commit.

        Args:
            repo_name (str): Repository name
            commit_sha (str): Commit SHA hash

        Returns:
            List[Dict]: List of merged PR data dictionaries
        """
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
        """Get a list of pull requests reviewed across all repositories.

        Returns:
            List[str]: List of formatted strings describing reviewed PRs
        """
        all_reviewed_prs = []

        for repo_name in REPOS:
            repo = GitHubRepo(repo_name)
            reviewed_prs = self._fetch_reviewed_prs(repo)
            all_reviewed_prs.extend(reviewed_prs)

        return all_reviewed_prs

    def _fetch_reviewed_prs(self, repo: GitHubRepo) -> List[str]:
        """Fetch reviewed pull requests from a repository.

        Args:
            repo (GitHubRepo): Repository to fetch from

        Returns:
            List[str]: List of formatted strings describing reviewed PRs
        """
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
