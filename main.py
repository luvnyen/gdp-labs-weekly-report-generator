import os
from datetime import datetime, timedelta

from core.weekly_report_generator import generate_weekly_report
from util.date_time_utils import format_duration
from util.progress_display_utils import ProgressDisplay

def get_week_dates():
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=4)  # Friday
    return start_of_week.date(), end_of_week.date()

def main():
    start_date, end_date = get_week_dates()

    print("\n📊 Weekly Report Generator")
    print(f"📅 Report period: {start_date} to {end_date}\n")

    progress = ProgressDisplay()
    progress.start()

    try:
        def progress_callback(task):
            progress.update_task(task)

        # Generate a report with progress updates
        report, total_duration = generate_weekly_report(
            progress_callback=progress_callback
        )

        # Stop the animation
        progress.stop_and_join()

        # Create output folder and save a report
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