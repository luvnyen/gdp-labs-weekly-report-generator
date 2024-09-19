# report_generator.py

import os
from crewai import Task

def generate_report(crew):
    result = crew.kickoff()
    print("\nDraft Report:\n")
    print(result)
    while True:
        if get_user_approval():
            break
        else:
            feedback = input("Please provide feedback for improvement: ")
            result = refine_report(crew, feedback)
            print("Report refinement complete")
    return result.raw

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
    crew.tasks[1] = refine_task
    return crew.kickoff()

def save_report(report, filename):
    os.makedirs('output', exist_ok=True)
    with open(os.path.join('output', filename), 'w') as f:
        f.write(report)
    print(f"Report saved to output/{filename}")