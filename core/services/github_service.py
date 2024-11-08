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
    """A class representing a GitHub repository with URL generation capabilities.

    This class provides methods to generate URLs for pull requests and commits
    within a specific GitHub repository.
    """

    def __init__(self, name: str) -> None:
        """Initialize GitHubRepo with repository name.

        Args:
            name (str): The name of the GitHub repository.
        """
        self.name = name
        self.pr_base_url = f"https://github.com/{REPO_OWNER}/{name}/pull"
        self.commit_base_url = f"https://github.com/{REPO_OWNER}/{name}/commit"

    def get_pr_url(self, pr_number: int) -> str:
        """Generate URL for a specific pull request.

        Args:
            pr_number (int): The pull request number.

        Returns:
            str: The complete URL to the pull request.
        """
        return f"{self.pr_base_url}/{pr_number}"

    def get_commit_url(self, commit_sha: str) -> str:
        """Generate URL for a specific commit.

        Args:
            commit_sha (str): The SHA hash of the commit.

        Returns:
            str: The complete URL to the commit.
        """
        return f"{self.commit_base_url}/{commit_sha}"


class GitHubService:
    """Service for interacting with GitHub API.

    This class provides methods to fetch and process information about pull requests,
    commits, and reviewing activities from GitHub repositories.
    """

    def __init__(self) -> None:
        """Initialize GitHubService with authentication headers and time settings.

        Sets up authentication headers using personal access token and initializes
        time-related variables for filtering weekly data.
        """
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

    @staticmethod
    def _get_start_of_week() -> datetime.date:
        """Get the date of the start of the current week (Monday).

        Returns:
            datetime.date: The date representing the start (Monday) of the current week.
        """
        today = datetime.now(timezone.utc).date()
        return today - timedelta(days=today.weekday())

    def _get_pr_details(self, repo_name: str, pr_number: int) -> Optional[Dict]:
        """Get detailed information about a specific pull request.

        Args:
            repo_name (str): The name of the repository.
            pr_number (int): The pull request number.

        Returns:
            Optional[Dict]: Dictionary containing pull request details if successful,
                          None if the request fails.

        Note:
            Prints an error message to console if the request fails.
        """
        url = f"{GITHUB_API_BASE_URL}/repos/{REPO_OWNER}/{repo_name}/pulls/{pr_number}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        print(f"Error fetching PR #{pr_number} for {repo_name}: {response.status_code}")
        return None

    def _get_pr_commits(self, repo_name: str, pr_number: int) -> List[Dict]:
        """Get commits from a specific pull request.

        Retrieves all commit from the specified pull request that was made by the
        authenticated user during the current week.

        Args:
            repo_name (str): The name of the repository.
            pr_number (int): The pull request number.

        Returns:
            List[Dict]: List of dictionaries containing commit information with keys:
                       - sha: commit hash
                       - message: commit message
                       - date: commit date

        Note:
            Prints an error message to console if the request fails.
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
                break

        return commits

    def _fetch_merged_prs(self, repo: GitHubRepo) -> List[str]:
        """Fetch merged pull requests from a repository.

        Retrieves all merged pull requests authored by the authenticated user
        since the start of the current week.

        Args:
            repo (GitHubRepo): Repository object containing repository information.

        Returns:
            List[str]: List of formatted strings representing merged pull requests.

        Note:
            Prints an error message to console if the request fails.
        """
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

    @staticmethod
    def _format_merged_prs(repo: GitHubRepo, prs: List[Dict]) -> List[str]:
        """Format merged pull requests into strings.

        Args:
            repo (GitHubRepo): Repository object containing repository information.
            prs (List[Dict]): List of pull request dictionaries to format.

        Returns:
            List[str]: List of formatted strings representing pull requests.

        Format examples:
            feat(core): title CATAPA-API#123
            refactor(core): impl auto-approve for `ClassType` CATAPA-API#789
        """
        formatted_prs = []
        for pr in prs:
            title = pr['title']
            pr_number = pr['number']
            pr_link = repo.get_pr_url(pr_number)

            formatted_pr = f"{title} [{repo.name}#{pr_number}]({pr_link})"
            formatted_prs.append(formatted_pr)

        return formatted_prs

    def _fetch_repo_prs_and_commits(self, repo: GitHubRepo) -> Tuple[List[Any], Dict[int, List[Any]]]:
        """Fetch PRs and their commits from a repository.

        Retrieves all pull requests authored by the authenticated user and their
        associated commits from the specified repository.

        Args:
            repo (GitHubRepo): Repository object containing repository information.

        Returns:
            Tuple[List[Any], Dict[int, List[Any]]]: A tuple containing:
                - List of pull request details
                - Dictionary mapping PR numbers to lists of commit information

        Note:
            - Only returns PRs updated since the start of the current week
            - Prints error message to console if request fails
            - Prints progress information about the number of PRs found
        """
        url = f"{GITHUB_API_BASE_URL}/search/issues"
        query = f"repo:{REPO_OWNER}/{repo.name} is:pr author:{GITHUB_USERNAME} sort:updated-desc"

        params = {
            "q": query,
            "per_page": 100
        }

        your_prs = []
        pr_commits = defaultdict(list)

        while url:
            response = requests.get(url, params=params, headers=self.headers)
            if response.status_code == 200:
                for issue in response.json()['items']:
                    pr_details = self._get_pr_details(repo.name, issue['number'])
                    if not pr_details:
                        continue

                    pr_date = datetime.strptime(
                        pr_details['updated_at'],
                        "%Y-%m-%dT%H:%M:%SZ"
                    ).replace(tzinfo=timezone.utc)

                    if pr_date < self.start_of_week_datetime:
                        return your_prs, pr_commits

                    commits = self._get_pr_commits(repo.name, issue['number'])
                    if commits:
                        your_prs.append(pr_details)
                        pr_commits[issue['number']] = commits

                url = response.links.get('next', {}).get('url')
                params = {} if url else None
            else:
                print(f"Error fetching PRs for {repo.name}: {response.status_code}")
                break

        return your_prs, pr_commits

    def _fetch_reviewed_prs(self, repo: GitHubRepo) -> List[str]:
        """Fetch reviewed pull requests from a repository.

        Retrieves all pull requests reviewed by the authenticated user (excluding
        their own PRs) that were updated since the start of the current week.

        Args:
            repo (GitHubRepo): Repository object containing repository information.

        Returns:
            List[str]: List of formatted strings representing reviewed pull requests.

        Note:
            Prints an error message to console if the request fails.
        """
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
        """Get formatted string of PRs and commits for all repositories.

        Retrieves and formats all pull requests and their associated commits
        across all configured repositories.

        Returns:
            str: A formatted string containing all PRs and commits, with the following structure:
                * PR Title [RepoName#PRNumber](PR URL)
                   * [CommitHash](Commit URL): Commit title
                      * Additional commit message details (if any)

        Note:
            - Only includes PRs and commits from the current week
            - Indents commit information under each PR
            - Adds additional indentation for commit message details
        """
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
        """Get a list of merged pull requests from all repositories.

        Retrieves all merged pull requests authored by the authenticated user
        across all configured repositories since the start of the current week.

        Returns:
            List[str]: List of formatted strings representing merged pull requests
                      from all repositories.
        """
        all_merged_prs = []
        for repo_name in REPOS:
            repo = GitHubRepo(repo_name)
            merged_prs = self._fetch_merged_prs(repo)
            all_merged_prs.extend(merged_prs)
        return all_merged_prs

    def get_reviewed_prs(self) -> List[str]:
        """Get a list of pull requests reviewed across all repositories.

        Retrieves all pull requests reviewed by the authenticated user (excluding
        their own PRs) across all configured repositories that were updated since
        the start of the current week.

        Returns:
            List[str]: List of formatted strings representing reviewed pull requests
                      from all repositories.
        """
        all_reviewed_prs = []
        for repo_name in REPOS:
            repo = GitHubRepo(repo_name)
            reviewed_prs = self._fetch_reviewed_prs(repo)
            all_reviewed_prs.extend(reviewed_prs)
        return all_reviewed_prs
