"""Weekly Report to Google Docs Synchronization Module

This module provides functionality to automatically push weekly report content from 
local Markdown files to connected Google Docs documents. It serves as a bridge between 
locally generated Markdown reports and their Google Docs counterparts, maintaining 
consistent content across platforms.

The module works by:
1. Finding the appropriate weekly report Markdown file in output directory
2. Extracting the author name from the report
3. Locating the corresponding Google Docs link from Gmail notifications that match the author
4. Extracting the Google Docs document ID from link
5. Updating the Google Docs document with the Markdown content

This automation ensures that weekly reports are properly archived in Google Docs
for team visibility and collaboration without manual copy-paste operations.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import base64
import datetime
import os
import re
from typing import Optional, Tuple

from config.config import TIMEZONE
from core.services.google_docs_service import extract_google_docs_id_from_url, update_google_docs_content
from core.services.google_service import get_google_service


def get_last_week_sunday_and_this_week_saturday() -> Tuple[str, str]:
    """Calculate and return the dates for last week's Sunday and this week's Saturday.

    This method derives the date range for the weekly report based on the current date.
    The range always spans from the previous Sunday to the upcoming Saturday, which
    represents a standard weekly reporting period.

    Returns:
        Tuple[str, str]: Formatted date strings for last week's Sunday and this week's
            Saturday in the format "DD Month YYYY" (e.g., "01 January 2023").
    """
    today = datetime.datetime.now(TIMEZONE).date()
    this_week_monday = today - datetime.timedelta(days=today.weekday())
    last_week_sunday = this_week_monday - datetime.timedelta(days=1)
    this_week_saturday = this_week_monday + datetime.timedelta(days=5)
    return last_week_sunday.strftime("%d %B %Y"), this_week_saturday.strftime("%d %B %Y")


def extract_author_name_from_report(report_path: str) -> Optional[str]:
    """Extract the author name from the weekly report markdown file.

    Parses the markdown file to find the author name from the title line.
    Expected format: # [Weekly Report: Author Name] Date Range

    Args:
        report_path (str): Path to the weekly report markdown file.

    Returns:
        Optional[str]: The extracted author name, or None if not found.
    """
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()

        match = re.search(r'\[Weekly Report:\s*([^\]]+)\]', first_line)
        if match:
            return match.group(1).strip()
    except Exception as e:
        print(f"Error extracting author name: {e}")

    return None


def find_gmail_with_weekly_report_link(author_name: str) -> Optional[str]:
    """Search Gmail for the weekly report email containing the Google Docs link for specific author.

    Queries the user's Gmail account for automated weekly report notification emails
    that contain links to the Google Docs where report content should be synced.
    The search uses date-specific subject lines and filters by author name in content.

    Args:
        author_name (str): The name of the report author to filter emails.

    Returns:
        Optional[str]: Message ID of the weekly report email for the author, or None if not found.
    """
    service = get_google_service('gmail', 'v1')
    last_week_sunday, this_week_saturday = get_last_week_sunday_and_this_week_saturday()
    subject = f"[Fill Weekly Report] {last_week_sunday} - {this_week_saturday}"
    query = f'from:agent@gdplabs.id subject:"{subject}"'

    results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        return None

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

        payload = msg.get('payload', {})
        parts = payload.get('parts', [])

        email_content = ''
        for part in parts:
            if part.get('mimeType') in ['text/html', 'text/plain'] and part['body'].get('data'):
                email_content += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

        if author_name and author_name.lower() in email_content.lower():
            return message['id']

    return None


def extract_google_docs_link_from_email(email_msg: dict) -> Optional[str]:
    """Extract the Google Docs link from a Gmail message payload.

    Parses the HTML and plain text content of a Gmail message to find Google Docs
    links for weekly reports. The method first looks for specifically formatted links
    with "Open Weekly Report" anchor text, then falls back to a more general search
    for any Google Docs document links if the specific format isn't found.

    Args:
        email_msg (dict): The Gmail message payload retrieved from the Gmail API.

    Returns:
        Optional[str]: The extracted Google Docs link, or None if not found.
    """
    payload = email_msg.get('payload', {})
    parts = payload.get('parts', [])

    html_content = ''
    for part in parts:
        if part.get('mimeType') == 'text/html' and part['body'].get('data'):
            html_content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            break

    if not html_content:
        for part in parts:
            if part.get('mimeType') == 'text/plain' and part['body'].get('data'):
                html_content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break

    if not html_content:
        return None

    match = re.search(
        r'href="(https://docs\.google\.com/document/d/[\w-]+/edit)"[^>]*>Open Weekly Report<',
        html_content
    )
    if match:
        return match.group(1)

    generic = re.search(r'(https://docs\.google\.com/document/d/[\w-]+/edit)', html_content)
    if generic:
        return generic.group(1)

    return None


class MarkdownToGoogleDocsSync:
    """Synchronize local Markdown reports with Google Docs.

    This class provides utilities to locate weekly report Markdown files and
    push their content to corresponding Google Docs documents. It handles the
    entire workflow from finding the latest report to locating the linked
    Google Docs via Gmail and updating the document's content.

    The synchronization process maintains consistency between local Markdown reports
    and their Google Docs counterparts, facilitating easier sharing and collaboration.

    Attributes:
        OUTPUT_DIR (str): Directory where weekly report Markdown files are stored.
        REPORT_PATTERN (str): Regex pattern to identify weekly report filenames.
    """

    OUTPUT_DIR = 'output'
    REPORT_PATTERN = r'^Weekly_Report_.*\.md$'

    def find_latest_weekly_report_md(self) -> Optional[str]:
        """Locate the most recent weekly report in Markdown format from the output directory.

        Scans the configured output directory for weekly report Markdown files and
        returns the path to the most recently modified file. This method is used when
        no specific report file is provided to the sync operation.

        Returns:
            Optional[str]: Path to the latest weekly report Markdown file, or None if not found.
        """
        if not os.path.isdir(self.OUTPUT_DIR):
            return None
        report_files = [
            os.path.join(self.OUTPUT_DIR, f) for f in os.listdir(self.OUTPUT_DIR)
            if f.startswith('Weekly_Report_') and f.endswith('.md')
        ]
        if not report_files:
            return None
        latest_report = max(report_files, key=os.path.getmtime)
        return latest_report

    def push_report_to_google_docs(self, report_path: Optional[str] = None) -> None:
        """Push weekly report Markdown content to its connected Google Docs document.

        The main orchestration function that handles the entire process of finding the
        appropriate weekly report, locating its linked Google Docs document via Gmail
        (filtered by author name), and updating the Google Docs content with the Markdown report.

        If no specific report path is provided, the method will use the most recently
        modified weekly report from the output directory.

        Args:
            report_path (Optional[str]): Path to the weekly report Markdown file. If None,
                                     the latest report in OUTPUT_DIR is used.
        """
        report_path = report_path or self.find_latest_weekly_report_md()
        print(f"📄 Using weekly report: {report_path}")

        author_name = extract_author_name_from_report(report_path)
        if not author_name:
            print("❌ Could not extract author name from report")
            return

        print(f"👤 Found author: {author_name}")

        msg_id = find_gmail_with_weekly_report_link(author_name)
        if not msg_id:
            print(f"❌ Could not find weekly report email for author: {author_name}")
            return

        gmail_service = get_google_service('gmail', 'v1')
        msg = gmail_service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        google_docs_link = extract_google_docs_link_from_email(msg)

        if not google_docs_link:
            print("❌ Could not extract Google Docs link from email")
            return

        doc_id = extract_google_docs_id_from_url(google_docs_link)

        with open(report_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        update_google_docs_content(doc_id, md_content)
        print(f"✅ Done. Weekly report pushed to Google Docs: {google_docs_link}")


if __name__ == "__main__":
    syncer = MarkdownToGoogleDocsSync()
    syncer.push_report_to_google_docs()