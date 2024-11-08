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

from config.config import GMAIL_SCOPES
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
            service = get_google_service('gmail', 'v1', 'token_gmail.json', GMAIL_SCOPES)

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
        service = get_google_service('gmail', 'v1', 'token_gmail.json', GMAIL_SCOPES)

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
            <html>
                <head>
                    <style>
                        body {{
                            font-family: trebuchet ms, sans-serif;
                            line-height: 1.6;
                            color: #333333;
                            max-width: 900px;
                            margin: 0 auto;
                            padding: 20px;
                            }}

                        h1, h2, h3, h4, h5, h6, a {{
                            color: #38761d;
                            font-weight: 700;
                            margin-top: 1.5em;
                            margin-bottom: 0.5em;
                        }}

                        a {{
                            text-decoration: none;
                        }}

                        a:hover {{
                            text-decoration: underline;
                        }}

                        hr {{
                            border: 0;
                            height: 1px;
                            background-color: #ddd;
                            margin: 20px 0;
                            }}

                        pre {{
                            background-color: #f5f5f5;
                            padding: 10px;
                            border-radius: 4px;
                            overflow-x: auto;
                            margin: 16px 0;
                        }}

                        code {{
                            background-color: #f5f5f5;
                            padding: 2px 4px;
                            border-radius: 4px;
                            font-family: monospace;
                        }}

                        p {{
                            margin: 16px 0;
                        }}

                        ul, ol {{
                            padding-left: 20px;
                            margin: 16px 0;
                        }}

                        li {{
                            margin: 8px 0;
                        }}

                        img {{
                            max-width: 100%;
                            height: auto;
                        }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
            </html>
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
