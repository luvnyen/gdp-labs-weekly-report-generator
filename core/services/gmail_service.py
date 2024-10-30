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

import markdown

from config.config import GMAIL_SCOPES
from core.services.google_service import get_google_service


def get_user_full_name(service=None):
    try:
        if service is None:
            service = get_google_service('gmail', 'v1', 'token_gmail.json', GMAIL_SCOPES)

        # Get the profile information
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', '')

        if not email:
            return 'Unknown User'

        # Get the part before @ and split by dots
        name_parts = email.split('@')[0].split('.')

        # Capitalize the first letter of each part
        formatted_parts = []
        for part in name_parts:
            if len(part) == 1:
                # If it's a single character (middle initial), make it uppercase and add a period
                formatted_parts.append(f"{part.upper()}.")
            else:
                # Otherwise capitalize the word
                formatted_parts.append(part.capitalize())

        return ' '.join(formatted_parts)

    except Exception as e:
        raise Exception(f"Failed to retrieve user's full name from Gmail: {str(e)}")

def get_date_range():
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=4)

    start_day = str(start_of_week.day)
    end_day = str(end_of_week.day)

    # Check if start and end dates are in the same month
    if start_of_week.month == end_of_week.month:
        return f"{start_of_week.strftime('%B')} {start_day}-{end_day}, {end_of_week.year}"
    else:
        # Different months
        return f"{start_of_week.strftime('%B')} {start_day} - {end_of_week.strftime('%B')} {end_day}, {end_of_week.year}"

def create_gmail_draft(report, to, cc, template):
    try:
        service = get_google_service('gmail', 'v1', 'token_gmail.json', GMAIL_SCOPES)

        # Get user's full name from Gmail
        try:
            author_full_name = get_user_full_name(service)
        except Exception:
            # Fallback to email address if name retrieval fails
            profile = service.users().getProfile(userId='me').execute()
            author_full_name = profile.get('emailAddress', 'Unknown User')

        date_range = get_date_range()

        # Convert lists to comma-separated strings
        to_str = ', '.join(to) if isinstance(to, list) else to
        cc_str = ', '.join(cc) if isinstance(cc, list) else cc

        # Convert Markdown to HTML
        content = template.format(date_range=date_range, report=report)
        html_content = markdown.markdown(content, extensions=['extra'])

        # Add some basic styling
        styled_html = f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
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
                        }}
                        code {{
                            background-color: #f5f5f5;
                            padding: 2px 4px;
                            border-radius: 4px;
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