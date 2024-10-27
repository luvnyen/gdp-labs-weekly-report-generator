from groq import Groq
import google.generativeai as genai
from config.config import GROQ_API_KEY, GOOGLE_GEMINI_API_KEY

# Prompt templates for different models
GROQ_SYSTEM_PROMPT = """<|start_header_id|>system<|end_header_id|>
You are an expert in summarizing Pull Requests and commit messages. You will receive a list of PRs and their associated commits, 
and you need to format them according to specific rules while maintaining consistent structure and formatting.

Here are the rules you must follow:
1. Format PR titles exactly as shown in the example
2. Extract and summarize key points from commit messages and its details into maximum 5 bullet points for Key Changes Implemented
3. Description must be a single sentence summary of the Key Changes Implemented
4. Format code-related terms with backticks
5. Maintain the exact structure (PR name, number, Description, Status, Key Changes)
6. Use PR title as Description and Key Changes Implemented if no commit details exist
7. Always use "leave_this_blank" for Status
8. Key Changes Implemented should be direct bullet points without sub-bullets

Format each PR according to this example structure:

* test(core): increase code coverage for `/core/personnel/api/v1` module [#18420](https://github.com/GDP-ADMIN/CATAPA-API/pull/18420)
    * **Description:** Enhanced test coverage through improved MSS integration, notification services, and null handling implementations.
    * **Status:** leave_this_blank
    * **Key Changes Implemented:**
        * Enhanced `MssEmployeeApiController` with `Optional`
        * Simplified notification config services using `map()`
        * Updated tests for better null handling and mocking

You should only return the formatted summary without any additional text or explanations.
<|eot_id|>"""

GROQ_USER_PROMPT = """<|start_header_id|>user<|end_header_id|>
Here are the PRs to summarize:
{content}
<|eot_id|>"""

GEMINI_PROMPT_TEMPLATE = """
Summarize the commit messages for each PR while maintaining the following rules:
1. Format the PR title exactly as shown in the example, including the PR number and link.
2. Extract and summarize key points from commit messages and its details into maximum 5 bullet points for Key Changes Implemented
3. Description must be a single sentence summary of the Key Changes Implemented
4. Format code-related terms with backticks
5. Maintain the exact structure of the example format (PR name, PR number with GitHub link, Description, Status, and Key Changes Implemented)
6. Use PR title as Description and Key Changes Implemented if no commit details exist
7. Always use "leave_this_blank" for the Status field
8. Key Changes Implemented should not have a sub-bullet point

Only provide the formatted output in your response.
Use the following format for each PR:

* test(core): increase code coverage for `/core/personnel/api/v1` module [#18420](https://github.com/GDP-ADMIN/CATAPA-API/pull/18420)
    * **Description:** Enhanced test coverage through improved MSS integration, notification services, and null handling implementations.
    * **Status:** leave_this_blank
    * **Key Changes Implemented:**
        * Enhanced `MssEmployeeApiController` with `Optional`
        * Simplified notification config services using `map()`
        * Updated tests for better null handling and mocking

Ensure that the description, status, and key changes implemented are indented one tab more than the PR title line. The PR title should include the exact title from the original list, followed by the PR number in square brackets, which is also a link to the PR.

Here are the PRs you need to summarize:
{content}"""

def summarize_with_groq(content):
    client = Groq(api_key=GROQ_API_KEY)
    
    formatted_user_prompt = GROQ_USER_PROMPT.format(content=content)
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": GROQ_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": formatted_user_prompt,
            }
        ],
        model="llama-3.2-3b-preview",
    )
    
    return chat_completion.choices[0].message.content

def summarize_with_gemini(content):
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    formatted_prompt = GEMINI_PROMPT_TEMPLATE.format(content=content)
    response = model.generate_content(formatted_prompt)
    
    return response.text

def summarize_accomplishments_with_llm(accomplishments):
    # Default to using Gemini
    return summarize_with_gemini(accomplishments)
    
    # Uncomment the line below and comment out the line above to use Groq instead
    # return summarize_with_groq(accomplishments)