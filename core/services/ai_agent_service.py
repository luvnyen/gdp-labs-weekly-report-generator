"""AI Agent Service for Report Enhancement

This module provides AI agent orchestration to enhance and refine weekly reports
using a crew of specialized AI agents.

Authors:
    - Glenn Steven Santoso (glenn.s.santoso@gdplabs.id)
"""

from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import GROQ_API_KEY, GOOGLE_GEMINI_API_KEY


class AIAgentReportService:
    """Service for enhancing reports using a crew of AI agents"""

    def __init__(self, use_groq=True):
        """Initialize the AI agent service with specified LLM choice"""
        self.use_groq = use_groq

    def _create_llm_agent(self, role, goal, backstory):
        """Create an AI agent with specified parameters"""
        if self.use_groq:
            llm = ChatGroq(
                model_name="groq/gemma2-9b-it",
                api_key=GROQ_API_KEY,
                verbose=True,
                temperature=0.5
            )
        else:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.0-pro",
                google_api_key=GOOGLE_GEMINI_API_KEY
            )

        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

    def create_agent_crew(self, report):
        """Create a crew of specialized AI agents for report enhancement"""
        # Content analyzer agent
        analyzer = self._create_llm_agent(
            role='Report Analyzer Agent',
            goal='Analyze the report content and identify areas for improvement',
            backstory='Expert technical editor with deep experience in developer reports and documentation, specializing in technical accuracy and clarity'
        )

        # Enhancement writer agent
        enhancer = self._create_llm_agent(
            role='Report Enhancement Agent',
            goal='Improve report clarity, structure, and presentation while preserving technical accuracy',
            backstory='Skilled technical writer specializing in clear, professional communication and data presentation'
        )

        # Quality assurance agent
        qa_agent = self._create_llm_agent(
            role='Report QA Agent',
            goal='Ensure report maintains accuracy while being enhanced',
            backstory='Detail-oriented editor focused on maintaining factual accuracy, data consistency, and technical precision'
        )

        # Create tasks for the agents
        analyze_task = Task(
            description="""
            Analyze this report and identify areas for improvement in clarity, structure, and presentation, 
            while preserving all factual content:

            """ + report + """

            Provide specific recommendations for improvements including:
            1. Structure and organization
            2. Clarity and readability
            3. Professional tone and consistency
            4. Data presentation
            5. Technical accuracy
            """,
            agent=analyzer,
            expected_output="Detailed analysis of areas for improvement with specific recommendations"
        )

        enhance_task = Task(
            description="""
            Using the analysis provided in the previous task and the original report, create an enhanced version
            that improves clarity and presentation while preserving all factual information.

            Original Report:
            """ + report + """

            Focus on implementing the recommended improvements from the analysis while ensuring all original data 
            and facts remain intact.
            """,
            agent=enhancer,
            expected_output="Enhanced version of the report with improved clarity and presentation",
            dependencies=[analyze_task]
        )

        qa_task = Task(
            description="""
            Review the original and enhanced reports to ensure accuracy and improvements.

            Original Report:
            """ + report + """

            Review the enhanced version from the previous task and verify:
            1. All factual information is preserved
            2. Data points remain accurate
            3. Technical content is correctly represented
            4. Improvements maintain document integrity

            If any issues are found, provide corrections while maintaining the enhanced structure.
            """,
            agent=qa_agent,
            expected_output="Final verified report with confirmation of factual accuracy",
            dependencies=[enhance_task]
        )

        # Create and return the crew
        return Crew(
            agents=[analyzer, enhancer, qa_agent],
            tasks=[analyze_task, enhance_task, qa_task],
            verbose=True
        )

    def process_report(self, report):
        """Process the given report using AI agent crew"""
        crew = self.create_agent_crew(report)

        # Initial enhancement
        result = crew.kickoff()
        enhanced_report = result.raw

        while True:
            print("\n\nAI Enhanced Report Draft:\n")
            print(enhanced_report)

            response = input("\n\nDo you approve this AI-enhanced report? (yes/no): ").lower()
            if response in ['yes', 'y']:
                break

            feedback = input("\n\nPlease provide feedback for the AI agents: ")
            enhanced_report = self._refine_with_agents(crew, enhanced_report, feedback)

        return enhanced_report

    def _refine_with_agents(self, crew, current_report, feedback):
        """Refine the report using AI agents based on user feedback"""
        refine_task = Task(
            description="""
            Refine this report based on the provided feedback while preserving all factual content.

            Current Report:
            """ + current_report + """

            User Feedback:
            """ + feedback + """

            Ensure all improvements maintain accuracy and data integrity while addressing the feedback.
            """,
            agent=crew.agents[1],  # Use the enhancement agent
            expected_output="Refined version of the report addressing the feedback while maintaining accuracy"
        )

        crew.tasks[1] = refine_task
        result = crew.kickoff()
        return result.raw