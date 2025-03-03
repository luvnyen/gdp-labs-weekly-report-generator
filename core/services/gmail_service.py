"""Gmail Service Module

This module provides functionality to interact with Gmail API for creating
and sending email drafts.

Authors:
    - Glenn Steven Santoso (glenn.s.santoso@gdplabs.id)
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from typing import Union, List, Dict, Any

import markdown
from googleapiclient.discovery import Resource

from core.services.google_service import get_google_service


def get_user_full_name(service: Resource | None = None) -> str:
    """Retrieve user's full name from Gmail profile.

    Formats the email address username into a proper name format.
    Single characters are treated as initials with periods.

    Args:
        service (Resource | None): Gmail API service instance.
        If None, create a new instance.

    Returns:
        str: Formatted full name or email address if formatting fails.

    Raises:
        Exception: If unable to retrieve user profile from Gmail.
    """
    try:
        if service is None:
            service = get_google_service('gmail', 'v1')

        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', '')

        if not email:
            return 'Unknown User'

        name_parts = email.split('@')[0].split('.')
        formatted_parts = []
        for part in name_parts:
            if len(part) == 1:
                formatted_parts.append(f"{part.upper()}.")
            else:
                formatted_parts.append(part.capitalize())

        return ' '.join(formatted_parts)

    except Exception as e:
        raise Exception(f"Failed to retrieve user's full name from Gmail: {str(e)}")


def get_date_range() -> str:
    """Generate a formatted date range string for the current work week.

    Returns:
        str: Formatted date range (e.g., "October 1-5, 2024" or
             "September 30 - October 4, 2024")
    """
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=4)

    start_day = str(start_of_week.day)
    end_day = str(end_of_week.day)

    if start_of_week.month == end_of_week.month:
        return f"{start_of_week.strftime('%B')} {start_day}-{end_day}, {end_of_week.year}"
    else:
        return f"{start_of_week.strftime('%B')} {start_day} - {end_of_week.strftime('%B')} {end_day}, {end_of_week.year}"


def create_gmail_draft(
        report: str,
        to: Union[str, List[str]],
        cc: Union[str, List[str]],
        template: str
) -> Dict[str, Any]:
    """Create a Gmail draft with weekly report content.

    Args:
        report (str): Report content in Markdown format
        to (Union[str, List[str]]): Recipient email(s)
        cc (Union[str, List[str]]): CC recipient email(s)
        template (str): Email template with {date_range} and {report} placeholders

    Returns:
        Dict[str, Any]: Created draft object from Gmail API

    Raises:
        Exception: If draft creation fails
    """
    try:
        service = get_google_service('gmail', 'v1')

        try:
            author_full_name = get_user_full_name(service)
        except Exception:
            profile = service.users().getProfile(userId='me').execute()
            author_full_name = profile.get('emailAddress', 'Unknown User')

        date_range = get_date_range()

        to_str = ', '.join(to) if isinstance(to, list) else to
        cc_str = ', '.join(cc) if isinstance(cc, list) else cc

        content = template.format(date_range=date_range, report=report)
        html_content = markdown.markdown(content, extensions=['extra'])

        styled_html = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px;">
            <style>
                h4 {{
                    margin-top: 20px;
                    margin-bottom: 10px;
                    font-size: 18px;
                    font-weight: bold;
                    color: #2c3e50;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 5px;
                }}
                ul {{
                    margin-top: 10px;
                    margin-bottom: 15px;
                    padding-left: 25px;
                }}
                li {{
                    margin-bottom: 5px;
                }}
                li ul {{
                    margin-top: 5px;
                }}
                p {{
                    margin-bottom: 10px;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                code {{
                    background-color: #f8f8f8;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: Consolas, Monaco, 'Andale Mono', monospace;
                    font-size: 90%;
                    color: #e74c3c;
                }}
                blockquote {{
                    border-left: 4px solid #ddd;
                    padding-left: 10px;
                    margin-left: 20px;
                    color: #777;
                }}
                .emoji {{
                    font-size: 1.2em;
                    vertical-align: middle;
                }}
                .small-text {{
                    font-size: 0.8em;
                    color: #888;
                    font-style: italic;
                }}
            </style>
            {html_content}
        </div>
        """

        message = MIMEText(styled_html, 'html')
        message['to'] = to_str
        message['cc'] = cc_str
        message['subject'] = f'[Weekly Report: {author_full_name}] {date_range}'

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        draft = service.users().drafts().create(userId='me', body={
            'message': {
                'raw': raw_message
            }
        }).execute()

        return draft

    except Exception as e:
        raise Exception(f"Failed to create Gmail draft: {str(e)}")
