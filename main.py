"""Weekly Report Generator Main Module

This module serves as the entry point for the weekly report generator application,
integrating traditional report generation with AI agent enhancement.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
    - Glenn Steven Santoso (glenn.s.santoso@gdplabs.id)
"""

import os
import time
from datetime import datetime, timedelta
from typing import Tuple

from core.weekly_report_generator import generate_weekly_report
from core.services.ai_agent_service import AIAgentReportService
from core.services.gmail_service import create_gmail_draft
from utils.date_time_util import format_duration
from utils.progress_display_util import ProgressDisplay
from config.config import GMAIL_SEND_TO, GMAIL_SEND_CC


def get_week_dates() -> Tuple[datetime.date, datetime.date]:
    """Get the date range for the current work week (Monday to Friday).

    Returns:
        Tuple[datetime.date, datetime.date]: Start date (Monday) and end date (Friday)
        of the current week
    """
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=4)  # Friday
    return start_of_week.date(), end_of_week.date()


def main() -> None:
    """Main entry point for the weekly report generator.

    - Determines the report date range (current week)
    - Initializes progress display
    - Generates the report with progress updates
    - Saves a report to Markdown file in 'output' directory
    - Handles errors and resource cleanup

    File naming format: Weekly_Report_YYYY-MM-DD_to_YYYY-MM-DD.md

    Raises:
        Exception: Re-raises any exceptions from report generation after cleanup
    """
    start_date, end_date = get_week_dates()
    start_time = time.time()

    print("\n📊 Weekly Report Generator")
    print(f"📅 Report period: {start_date} to {end_date}\n")

    progress = ProgressDisplay()
    progress.start()

    try:
        def progress_callback(task: str) -> None:
            progress.update_task(task)

        # Generate an initial report with progress updates
        initial_report, initial_duration = generate_weekly_report(
            progress_callback=progress_callback,
            create_draft=False  # Don't create draft yet, wait for AI-enhanced version
        )

        # Enhance report using AI agents
        progress.update_task("Enhancing report with AI agent crew")
        ai_service = AIAgentReportService()
        enhanced_report = ai_service.process_report(initial_report)

        # Stop the animation
        progress.stop_and_join()

        # Create output folder and save both versions of the report
        output_folder = 'output'
        os.makedirs(output_folder, exist_ok=True)

        # Save initial report
        initial_filename = f'Weekly_Report_Initial_{start_date}_to_{end_date}.md'
        initial_filepath = os.path.join(output_folder, initial_filename)
        with open(initial_filepath, 'w') as f:
            f.write(initial_report)

        # Save AI-enhanced report
        enhanced_filename = f'Weekly_Report_AI_Enhanced_{start_date}_to_{end_date}.md'
        enhanced_filepath = os.path.join(output_folder, enhanced_filename)
        with open(enhanced_filepath, 'w') as f:
            f.write(enhanced_report)

        # Create Gmail draft with enhanced version
        # progress.update_task("Creating Gmail draft")
        # create_gmail_draft(enhanced_report, GMAIL_SEND_TO, GMAIL_SEND_CC)

        total_duration = time.time() - start_time
        print(f"\n✨ Report generation and AI enhancement completed in {format_duration(total_duration)}")
        print(f"📝 Initial report saved to: {initial_filepath}")
        print(f"📝 AI-enhanced report saved to: {enhanced_filepath}")
        print("📧 Gmail draft created with AI-enhanced report\n")

    except Exception as e:
        progress.stop_and_join()
        print(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
