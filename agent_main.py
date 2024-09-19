# agent_main.py

import os
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# Import existing utilities
from weekly_report_generator import generate_weekly_report
from github_utils import get_prs_and_commits, get_merged_prs, get_reviewed_prs
from google_calendar_utils import get_events_for_week
from sonarqube_utils import get_test_coverage
from config import REPO_OWNER, REPO_NAME, GROQ_API_KEY, GOOGLE_GEMINI_API_KEY
from api_utils import create_gmail_draft, create_google_sites_draft

load_dotenv()

def create_llm_agent(role, goal, backstory, use_groq=True):
    if use_groq:
        llm = ChatGroq(model_name="groq/gemma2-9b-it", api_key=GROQ_API_KEY, verbose=True, temperature=0.5)
    else:
        llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro", google_api_key=GOOGLE_GEMINI_API_KEY)

    
    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        verbose=True,
        llm=llm
    )

def collect_all_data():
    print("Collecting data...")
    github_prs, github_commits = get_prs_and_commits()
    print("GitHub data collected.")
    github_merged_prs = get_merged_prs()
    print("GitHub merged PRs collected.")
    github_reviewed_prs = get_reviewed_prs()
    print("GitHub reviewed PRs collected.")
    calendar_events = get_events_for_week()
    print("Calendar events collected.")
    sonarqube_coverage = get_test_coverage()
    print("SonarQube data collected.")
    
    return {
        'github_prs': github_prs,
        'github_commits': github_commits,
        'github_merged_prs': github_merged_prs,
        'github_reviewed_prs': github_reviewed_prs,
        'calendar_events': calendar_events,
        'sonarqube_coverage': sonarqube_coverage
    }

def create_agents_and_tasks(collected_data):
    data_compiler = create_llm_agent(
        role='Data Compiler',
        goal='Compile all collected data into a structured format for the weekly report',
        backstory='Expert in organizing and structuring diverse datasets from multiple sources',
        use_groq=True
    )
    
    report_writer = create_llm_agent(
        role='Report Writer',
        goal='Create a comprehensive weekly report based on compiled data',
        backstory='Experienced technical writer specializing in clear, concise developer reports',
        use_groq=True
    )
    
    compile_task = Task(
        description=f'Compile and structure the following data for the weekly report: {collected_data}',
        agent=data_compiler,
        expected_output="A structured and organized compilation of the provided data, ready for report writing."
    )
    
    with open('TEMPLATE.md', 'r') as template_file:
        template = template_file.read()
    
    write_report_task = Task(
        description=f'Write the weekly report based on the compiled data. Use the following template: {template}',
        agent=report_writer,
        expected_output="A complete weekly report following the provided template, incorporating all the compiled data."
    )
    
    return [data_compiler, report_writer], [compile_task, write_report_task]

def get_user_approval():
    while True:
        response = input("Do you approve this report? (yes/no): ").lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please answer with 'yes' or 'no'.")

def refine_report(crew, feedback):
    refine_task = Task(
        description=f'Refine the report based on the following user feedback: {feedback}',
        agent=crew.agents[1],  # Assuming the report writer is the second agent
        expected_output="An improved version of the report addressing the user's feedback."
    )
    return crew.kickoff(tasks=[refine_task])

def save_report(report, filename):
    os.makedirs('output', exist_ok=True)
    with open(os.path.join('output', filename), 'w') as f:
        f.write(report)
    print(f"Report saved to output/{filename}")

def get_week_dates():
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=4)
    return start_of_week.date(), end_of_week.date()

def main():
    start_date, end_date = get_week_dates()
    print(f"Generating weekly report for {start_date} to {end_date}")
    
    collected_data = collect_all_data()
    agents, tasks = create_agents_and_tasks(collected_data)
    
    crew = Crew(agents=agents, tasks=tasks)
    
    while True:
        result = crew.kickoff()
        print("\nDraft Report:\n")
        print(result)
        
        if get_user_approval():
            break
        else:
            feedback = input("Please provide feedback for improvement: ")
            result = refine_report(crew, feedback)
    
    filename = f'Weekly_Report_{start_date}_to_{end_date}.md'
    save_report(result, filename)
    
    # Create Gmail draft
    try:
        create_gmail_draft(
            result,
            to="sahat.n.simangunsong@gdplabs.id",
            cc="ai@gdplabs.id, bosa-eng@gdplabs.id"
        )
        print("Gmail draft created successfully.")
    except Exception as e:
        print(f"Error creating Gmail draft: {str(e)}")
    
    # Create Google Sites draft
    try:
        create_google_sites_draft(
            result,
            site_id=os.getenv('GOOGLE_SITE_ID'),
            page_name=f"Weekly Report {start_date} to {end_date}"
        )
        print("Google Sites draft created successfully.")
    except Exception as e:
        print(f"Error creating Google Sites draft: {str(e)}")
    
    print("Weekly report generation complete!")

if __name__ == "__main__":
    main()