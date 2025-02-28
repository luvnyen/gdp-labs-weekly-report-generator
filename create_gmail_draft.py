"""Gmail Draft Creator Module

This module serves as an entry point for creating Gmail drafts from existing
weekly report Markdown files without generating a new report.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import argparse
import os
import sys
from typing import Optional

from config.config import ServiceType, config_manager
from core.services.gmail_service import create_gmail_draft
from core.user_data import GMAIL_TEMPLATE


def find_latest_report() -> Optional[str]:
    """Find the most recent weekly report file in the output directory.

    Returns:
        Optional[str]: Path to the latest report file or None if not found
    """
    output_dir = 'output'
    if not os.path.isdir(output_dir):
        return None

    report_files = [
        os.path.join(output_dir, f) for f in os.listdir(output_dir)
        if f.startswith('Weekly_Report_') and f.endswith('.md')
    ]

    if not report_files:
        return None

    latest_report = max(report_files, key=os.path.getmtime)
    return latest_report


def create_draft(report_path: str) -> bool:
    """Create a Gmail draft from an existing report file.

    Args:
        report_path (str): Path to the report Markdown file

    Returns:
        bool: True if successful, False otherwise
    """
    if not config_manager.is_service_available(ServiceType.GMAIL):
        print('❌ Error: Gmail integration not configured')
        return False

    try:
        with open(report_path, 'r') as f:
            report_content = f.read()
    except Exception as e:
        print(f'❌ Error reading report file: {str(e)}')
        return False

    gmail_config = config_manager.get_service_vars(ServiceType.GMAIL)
    to_emails = gmail_config['GMAIL_SEND_TO'].split(',')
    cc_emails = gmail_config.get('GMAIL_SEND_CC', '').split(',')

    try:
        draft = create_gmail_draft(
            report_content,
            to_emails,
            cc_emails,
            GMAIL_TEMPLATE
        )
        print('✅ Gmail draft created successfully')
        print(f'💡 Draft ID: {draft.get("id")}')
        return True
    except Exception as e:
        print(f'❌ Error creating Gmail draft: {str(e)}')
        return False


def main() -> None:
    """Main entry point for the Gmail draft creator.

    Parses command line arguments to determine which report file to use,
    or finds the most recent one if not specified.
    """
    parser = argparse.ArgumentParser(description='Create Gmail draft from weekly report')
    parser.add_argument('-f', '--file', help='Path to the markdown report file')
    args = parser.parse_args()

    report_path = args.file
    if not report_path:
        report_path = find_latest_report()
        if not report_path:
            print("❌ Error: No weekly report found in the output directory.")
            print("Please run the main script to generate a report first.")
            sys.exit(1)

    print("📨 Gmail Draft Creator")
    print(f"📄 Using report: {report_path}")

    success = create_draft(report_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()