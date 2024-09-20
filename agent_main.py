# agent_main.py

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Crew

from agents.data_collector import collect_all_data
from agents.data_preprocessor import preprocess_data
from agents.agent_creator import create_agents_and_tasks
from agents.report_generator import generate_report, save_report
from agents.utils.api import create_gmail_draft
from config import GMAIL_SEND_TO, GMAIL_SEND_CC

load_dotenv()

def get_week_dates():
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=4)
    return start_of_week.date(), end_of_week.date()

def main():
    start_date, end_date = get_week_dates()
    print(f"Generating weekly report for {start_date} to {end_date}")
    
    collected_data = collect_all_data()
    preprocessed_data = preprocess_data(collected_data)
    agents, tasks = create_agents_and_tasks(preprocessed_data)
    
    crew = Crew(agents=agents, tasks=tasks, verbose=True)
    report = generate_report(crew)
    
    filename = f'Weekly_Report_{start_date}_to_{end_date}.md'
    save_report(report, filename)
    
    # TODO: Implement sending the report via email and creating a Google Sites draft
    # Needs to check the Google oAuth consent screen, because it is not yet working as expected
    try:
        create_gmail_draft(
            report,
            to=GMAIL_SEND_TO,
            cc=GMAIL_SEND_CC
        )
        print("Gmail draft created successfully.")
    except Exception as e:
        print(f"Error creating Gmail draft: {str(e)}")
    
    print("Weekly report generation complete!")

if __name__ == "__main__":
    main()