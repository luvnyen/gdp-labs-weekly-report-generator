# agent_main.py

import os
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# Import existing utilities
from weekly_report_generator import generate_weekly_report, format_accomplishments, format_deployments, format_reviewed_prs, format_meetings, format_wfo_days
from github_utils import get_prs_and_commits, get_merged_prs, get_reviewed_prs
from google_calendar_utils import get_events_for_week
from sonarqube_utils import get_test_coverage
from config import REPO_OWNER, REPO_NAME, GROQ_API_KEY, GOOGLE_GEMINI_API_KEY
from api_utils import create_gmail_draft, create_google_sites_draft
import user_input

load_dotenv()

def create_llm_agent(role, goal, backstory, use_groq=True, allow_delegation=False):
    if use_groq:
        llm = ChatGroq(model_name="groq/gemma2-9b-it", api_key=GROQ_API_KEY, verbose=True, temperature=0.5)
    else:
        llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro", google_api_key=GOOGLE_GEMINI_API_KEY)
    
    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        verbose=True,
        allow_delegation=allow_delegation,
        llm=llm
    )

def preprocess_data(collected_data):
    print("Preprocessing data...")
    current_date = datetime.now()
    current_month = current_date.strftime("%B")
    current_year = current_date.year
    is_h2 = current_date.month > 6
    half_year = "H2" if is_h2 else "H1"
    half_year_year = current_year if is_h2 else current_year

    preprocessed_data = {
        'issues': format_list(user_input.issues, indent=""),
        'half_year': half_year,
        'half_year_year': half_year_year,
        'current_month': current_month,
        'current_year': current_year,
        'major_bugs_current_month': user_input.major_bugs_current_month,
        'minor_bugs_current_month': user_input.minor_bugs_current_month,
        'major_bugs_half_year': user_input.major_bugs_half_year,
        'minor_bugs_half_year': user_input.minor_bugs_half_year,
        'test_coverage': collected_data['sonarqube_coverage'],
        'accomplishments': format_accomplishments(collected_data['github_prs'], collected_data['github_commits']),
        'deployments': format_deployments(collected_data['github_merged_prs']),
        'prs_reviewed': format_reviewed_prs(collected_data['github_reviewed_prs']),
        'meetings_and_activities': format_meetings(collected_data['calendar_events']),
        'wfo_days': format_wfo_days(user_input.wfo_days),
        'next_steps': format_list(user_input.next_steps, indent=""),
        'learning': format_list(user_input.learning, indent="")
    }
    print("Data preprocessing complete.")
    return preprocessed_data

def format_list(items, indent=""):
    if not items:
        return f"{indent}* None"
    return '\n'.join(f"{indent}* {item}" for item in items)

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

def create_agents_and_tasks(preprocessed_data):
    data_analyzer = create_llm_agent(
        role='Data Analyzer',
        goal='Analyze the preprocessed data and extract key insights',
        backstory='Expert data analyst specializing in software development metrics and team performance',
        use_groq=True
    )
    
    report_writer = create_llm_agent(
        role='Report Writer',
        goal='Create a comprehensive weekly report based on analyzed data and insights',
        backstory='Experienced technical writer specializing in clear, concise developer reports',
        use_groq=True
    )
    
    quality_assurance = create_llm_agent(
        role='Quality Assurance Specialist',
        goal='Ensure the report meets high-quality standards and addresses all required sections',
        backstory='Meticulous editor with a keen eye for detail and consistency in technical documentation',
        use_groq=True
    )
    
    analyze_task = Task(
        description=f'Analyze the following preprocessed data and extract key insights: {preprocessed_data}',
        agent=data_analyzer,
        expected_output="A detailed analysis of the preprocessed data, highlighting key insights and trends. Detailed list of urls and links are also recommended, because it will be used in the report.",
        human_input=True
    )
    
    with open('TEMPLATE.md', 'r') as template_file:
        template = template_file.read()
    
    write_report_task = Task(
        description=f'Write the weekly report based on the analyzed data and insights. Use the following template: {template}',
        agent=report_writer,
        expected_output="A complete weekly report following the provided template, incorporating all the analyzed data and insights. Detailed list of urls and links are also recommended, because it will be used in the report.",
        human_input=True,
    )
    
    qa_task = Task(
        description='Review the written report for quality, consistency, and completeness. Ensure all sections are properly addressed.',
        agent=quality_assurance,
        expected_output="A reviewed and polished version of the report, with any necessary corrections or improvements."
    )
    
    return [data_analyzer, report_writer, quality_assurance], [analyze_task, write_report_task, qa_task]

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
    preprocessed_data = preprocess_data(collected_data)
    agents, tasks = create_agents_and_tasks(preprocessed_data)
    
    crew = Crew(agents=agents, tasks=tasks, verbose=True)
    
    result = crew.kickoff()
    print("\nDraft Report:\n")
    print(result)
    # while True:
    #     result = crew.kickoff()
    #     print("\nDraft Report:\n")
    #     print(result)
    #     # print(f"\nType of raw is {type(result.raw)}")
    #     # print(f"Result of raw is {result.raw}")
    #     # print(f"\nType of pydantic is {type(result.pydantic)}")
    #     # print(f"Result of pydantic is {result.pydantic}")
    #     # print(f"\nType of json_dict is {type(result.json_dict)}")
    #     # print(f"Result of json_dict is {result.json_dict}")
    #     # print(f"\nType of tasks_output is {type(result.tasks_output)}")
    #     # print(f"Result of tasks_output is {result.tasks_output}")

        
    #     if get_user_approval():
    #         break
    #     else:
    #         feedback = input("Please provide feedback for improvement: ")
    #         result = refine_report(crew, feedback)
    
    filename = f'Weekly_Report_{start_date}_to_{end_date}.md'
    save_report(result.raw, filename)
    
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