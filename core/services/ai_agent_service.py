"""AI Agent Service for Report Enhancement

This module provides AI agent orchestration to enhance and refine weekly reports
using a crew of specialized AI agents.

Authors:
    - Glenn Steven Santoso (glenn.s.santoso@gdplabs.id)
"""

from typing import Dict
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from crewai_tools import FileReadTool
from config.config import ConfigManager

# Template reader only for the analyzer
template_reader = FileReadTool(
    file_path='templates/template.md',
    description='A tool to read the report template file.'
)

@CrewBase
class AIAgentReportService:
    """Service for enhancing reports using a crew of AI agents"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, inputs: Dict) -> None:
        self.inputs = inputs
        self.config = ConfigManager()
        self.groq_model = ChatGroq(
            groq_api_key=self.config.groq_api_key,
            model_name="groq/deepseek-r1-distill-llama-70b",
            temperature=0.7,
            max_tokens=4096,
            streaming=True,
            verbose=True,
            max_retries=3
        )

        # TODO: Debug why openrouter doesn't work
        self.openrouter_model = ChatOpenAI(
            openai_api_key=self.config.openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model_name="deepseek/deepseek-chat:free",
            temperature=0.7,
            max_tokens=4096,
            streaming=True,
            verbose=True,
            max_retries=3,
        )

    @agent
    def content_analyzer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['content_analyzer_agent'],
            llm=self.groq_model,
            tools=[template_reader],  # Only the analyzer gets the template tool
            verbose=True
        )
    
    @agent
    def enhancement_writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['enhancement_writer_agent'],
            llm=self.groq_model,
            verbose=True  # No tools for the writer
        )
    
    @agent
    def qa_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['qa_agent'],
            llm=self.groq_model,
            verbose=True  # No tools for the QA agent
        )

    @task
    def analyze_content_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_content_task'],
            agent=self.content_analyzer_agent()
        )

    @task
    def enhance_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['enhance_report_task'],
            agent=self.enhancement_writer_agent()
        )

    @task
    def quality_check_task(self) -> Task:
        return Task(
            config=self.tasks_config['quality_check_task'],
            agent=self.qa_agent()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

def enhance_report_with_ai_agents(initial_report: str):
    # TODO: Run functionality
    print("\nChoose your report enhancement style:")
    print("1. Cheerful and Emoji-Enhanced ✨")
    print("2. Professional and Formal 📝")
    print("3. No Changes Needed ⏭️")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            if choice in [1, 2, 3]:
                break
            print("Please enter 1, 2, or 3")
        except ValueError:
            print("Please enter a valid number")
    
    style_mapping = {
        1: "Cheerful and Emoji-Enhanced",
        2: "Professional and Formal",
        3: "No Changes"
    }
    
    inputs = {
        'raw_report': initial_report,
        'style_preference': style_mapping[choice],
        'iteration_feedback': None
    }
    
    crew_instance = AIAgentReportService(inputs)
    
    while True:
        result = crew_instance.crew().kickoff(inputs=inputs)
        content = result.raw
        
        # Remove any "Final Answer" or similar text
        if "Final Answer" in content:
            content = content.replace("Final Answer", "").strip()
        
        print(f"\nEnhanced Report Draft ({style_mapping[choice]}):\n")
        print(content)
        
        response = input("\nDo you approve this enhanced report? (yes/no): ").lower()
        if response in ['yes', 'y']:
            break
            
        feedback = input("\nPlease provide feedback for improvement: ")
        inputs['iteration_feedback'] = feedback

    return content