"""Weekly Report Generator Main Module

This module serves as the entry point for the weekly report generator application,
handling command line interface and orchestrating the report generation process.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import os
from datetime import datetime, timedelta
from typing import Tuple

from core.weekly_report_generator import generate_weekly_report
from utils.date_time_util import format_duration
from utils.progress_display_util import ProgressDisplay


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

    print("\n📊 Weekly Report Generator")
    print(f"📅 Report period: {start_date} to {end_date}\n")

    progress = ProgressDisplay()
    progress.start()

    try:
        def progress_callback(task: str) -> None:
            progress.update_task(task)

        report, total_duration = generate_weekly_report(
            progress_callback=progress_callback
        )

        progress.stop_and_join()

        output_folder = 'output'
        os.makedirs(output_folder, exist_ok=True)
        filename = f'Weekly_Report_{start_date}_to_{end_date}.md'
        filepath = os.path.join(output_folder, filename)
        with open(filepath, 'w') as f:
            f.write(report)

        print(f"\n✨ Report generation completed in {format_duration(total_duration)}")
        print(f"📝 Report saved to: {filepath}\n")

    except Exception as e:
        progress.stop_and_join()
        print(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
