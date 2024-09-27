
from crewai import Agent, Task
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GROQ_API_KEY, GOOGLE_GEMINI_API_KEY

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
        backstory='Experienced technical writer specializing in clear, concise developer reports. Not only a concise writer, but also a good editor and a very expressve person, you are not shy in expressing friendly words. Likes to use catchy phrases and uses emoji to make it so flashy',
        use_groq=True,
    )
    
    quality_assurance = create_llm_agent(
        role='Quality Assurance Specialist',
        goal='Ensure the report meets high-quality standards and addresses all required sections',
        backstory='Meticulous editor with a keen eye for detail and consistency in technical documentation. A radiant and expressive person who loves to use emojis and friendly words. You are not shy in expressing your thoughts and feelings.',
        use_groq=True
    )
    
    with open('TEMPLATE.md', 'r') as template_file:
        template = template_file.read()

    analyze_task = Task(
        description=f'Analyze the following preprocessed data and extract key insights: {preprocessed_data} and you can refer to this template file to see the structure of the report and fit the data you have analyzed: {template}',
        agent=data_analyzer,
        expected_output="A detailed analysis of the preprocessed data, highlighting key insights and trends. Detailed list of urls and links are also recommended, because it will be used in the report.",
    )
    
    write_report_task = Task(
        description=f'Write the weekly report based on the analyzed data and insights. The report must only be based with the preprocessed data from Data Analyzer and you must not improvise too much. Use only and only the following template: {template}',
        agent=report_writer,
        expected_output="A complete weekly report following the provided template, incorporating all the analyzed data and insights. Detailed list of urls and links are also recommended, because it will be used in the report.",
    )
    
    qa_task = Task(
        description='Review the written report for quality, consistency, and completeness. Ensure all sections are properly addressed.',
        agent=quality_assurance,
        expected_output="A reviewed and polished version of the report, with any necessary corrections or improvements."
    )
    
    return [data_analyzer, report_writer, quality_assurance], [analyze_task, write_report_task, qa_task]