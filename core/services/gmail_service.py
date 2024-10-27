"""Gmail Service Module

This module provides functionality to interact with Gmail API for creating
and sending email drafts.

Authors:
    - Glenn Steven Santoso (glenn.s.santoso@gdplabs.id)
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

from datetime import datetime, timedelta
from email.mime.text import MIMEText
import base64
import markdown
from core.services.google_service import get_google_service
from config.config import AUTHOR_FULL_NAME, GMAIL_SCOPES

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
    service = get_google_service('gmail', 'v1', 'token_gmail.json', GMAIL_SCOPES)

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
    message['subject'] = f'[Weekly Report: {AUTHOR_FULL_NAME}] {date_range}'

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    draft = service.users().drafts().create(userId='me', body={
        'message': {
            'raw': raw_message
        }
    }).execute()

    return draft