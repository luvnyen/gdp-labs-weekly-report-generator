"""Weekly Report Generator Main Module

This module serves as the entry point for the weekly report generator application,
handling command line interface and orchestrating the report generation process.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import os
from datetime import datetime, timedelta, date
from typing import Tuple

from core.weekly_report_generator import generate_weekly_report
from core.user_data import REPORT_START_DATE, REPORT_END_DATE
from utils.date_time_util import format_duration
from utils.progress_display_util import ProgressDisplay


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Parsed date object
        
    Raises:
        ValueError: If date string is not in correct format
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Please use YYYY-MM-DD format.")


def get_week_dates() -> Tuple[datetime.date, datetime.date]:
    """Get the date range for the report period from user_data.py or current week.

    Returns:
        Tuple[datetime.date, datetime.date]: Start date and end date of the report period
        
    Raises:
        ValueError: If date format in user_data.py is invalid
    """
    start_date = REPORT_START_DATE
    end_date = REPORT_END_DATE
    
    if start_date and end_date:
        # User provided custom date range in user_data.py
        try:
            start = parse_date(start_date)
            end = parse_date(end_date)
            
            if start > end:
                raise ValueError("Start date must be before or equal to end date")
                
            return start, end
        except ValueError as e:
            raise ValueError(f"Invalid date format in user_data.py: {e}")
    elif start_date:
        # User provided only start date, use current week Friday as end
        try:
            start = parse_date(start_date)
            today = datetime.now()
            end_of_week = today - timedelta(days=today.weekday()) + timedelta(days=4)  # Friday
            return start, end_of_week.date()
        except ValueError as e:
            raise ValueError(f"Invalid start date format in user_data.py: {e}")
    elif end_date:
        # User provided only end date, use current week Monday as start
        try:
            end = parse_date(end_date)
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())  # Monday
            return start_of_week.date(), end
        except ValueError as e:
            raise ValueError(f"Invalid end date format in user_data.py: {e}")
    else:
        # No dates provided, use current week (Monday to Friday)
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=4)  # Friday
        return start_of_week.date(), end_of_week.date()


def main() -> None:
    """Main entry point for the weekly report generator.

    - Determines the report date range from user_data.py (custom period) or current week (default)
    - Initializes progress display
    - Generates the report with progress updates
    - Saves a report to Markdown file in 'output' directory
    - Handles errors and resource cleanup

    File naming format: Weekly_Report_YYYY-MM-DD_to_YYYY-MM-DD.md

    Raises:
        Exception: Re-raises any exceptions from report generation after cleanup
    """
    try:
        start_date, end_date = get_week_dates()
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please check the REPORT_START_DATE and REPORT_END_DATE variables in core/user_data.py")
        print("Use YYYY-MM-DD format (e.g., '2025-01-01') or set to None for current week")
        return

    print("📊 Weekly Report Generator")
    print(f"📅 Report period: {start_date} to {end_date}")
    if REPORT_START_DATE or REPORT_END_DATE:
        print("📝 Using custom date range from user_data.py")
    else:
        print("📝 Using current week (Monday to Friday)")
    print()

    progress = ProgressDisplay()
    progress.start()

    try:
        def progress_callback(task: str) -> None:
            progress.update_task(task)

        report, total_duration = generate_weekly_report(
            start_date=start_date,
            end_date=end_date,
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
