import time
import sys
import os
import threading
from datetime import datetime, timedelta
from weekly_report_generator import generate_weekly_report

def progress_animation():
    animation = "|/-\\"
    idx = 0
    while True:
        yield animation[idx % len(animation)]
        idx += 1

def get_week_dates():
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=4)  # Friday
    return start_of_week.date(), end_of_week.date()

def animate_progress(stop):
    spinner = progress_animation()
    while not stop.is_set():
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
    sys.stdout.write(' \b')

def main():
    start_date, end_date = get_week_dates()
    
    print("Generating weekly report")
    print(f"Report period: {start_date} to {end_date}")
    
    # Create a threading Event to signal when to stop the animation
    stop_animation = threading.Event()
    
    # Create a variable to store the report
    report = []

    # Function to generate report and set the stop flag
    def generate_and_store_report():
        nonlocal report
        report = generate_weekly_report()
        stop_animation.set()

    # Start report generation in a separate thread
    report_thread = threading.Thread(target=generate_and_store_report)
    report_thread.start()
    
    # Run animation until report generation is complete
    animate_progress(stop_animation)
    
    # Wait for report generation to finish
    report_thread.join()
    
    print("\nReport generation complete!")

    # Create output folder if it doesn't exist
    output_folder = 'output'
    os.makedirs(output_folder, exist_ok=True)

    # Save the report to a file in the output folder
    filename = f'Weekly_Report_{start_date}_to_{end_date}.md'
    filepath = os.path.join(output_folder, filename)
    with open(filepath, 'w') as f:
        f.write(report)

    print(f"Report saved to {filepath}")

if __name__ == "__main__":
    main()