from groq import Groq
import google.generativeai as genai
from config import GROQ_API_KEY, GOOGLE_GEMINI_API_KEY

def summarize_with_groq(content):
    client = Groq(api_key=GROQ_API_KEY)
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        model="gemma2-9b-it",
    )
    
    return chat_completion.choices[0].message.content

def summarize_with_gemini(content):
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    response = model.generate_content(content)
    
    return response.text

def summarize_accomplishments_with_llm(accomplishments):
    example_output_format = """
* test(core): increase code coverage for `/core/personnel/api/v1` module [#18420](https://github.com/GDP-ADMIN/CATAPA-API/pull/18420)
    * **Description:** Enhanced MSS and notification services, improving test coverage.
    * **Status:** leave_this_blank
    * **Key Changes Implemented:**
        * Enhanced `MssEmployeeApiController` with `Optional`
        * Simplified notification config services using `map()`
        * Updated tests for better null handling and mocking

* chore(core, common): improve `BaseIntegrationTest` and `ApprovalConstant` [#18434](https://github.com/GDP-ADMIN/CATAPA-API/pull/18434)
    * **Description:** Increase core personnel module to reach the target (97%)
    * **Status:** leave_this_blank
    * **Key Changes Implemented:**
        * Add new constants in `ApprovalConstant` for better endpoint management
        * Refactor `BaseIntegrationTest` for improved readability and maintainability
        * Use AssertJ's `assertThat` for assertions instead of JUnit's `assertEquals`
        * Simplify and standardize test helper methods
    """

    user_prompt = f"""
Summarize the commit messages for each PR while maintaining the following rules:
1. Format the PR title exactly as shown in the example, including the PR number and link.
2. Convert descriptions to past tense and make them concise.
3. Summarize the commit messages and descriptions, just take the important points, and put them in the Key Changes Implemented section.
4. Format words related to code using backticks.
5. Maintain the exact structure of the example format (PR name, PR number with GitHub link, Description, Status, and Key Changes Implemented).
6. If a PR has no commit details, use the PR title as Description and Key Changes Implemented.
7. Always use "leave_this_blank" for the Status field.
8. Key Changes Implemented should not have a sub-bullet point.

Only provide the formatted output in your response.
Use the following format for each PR:
{example_output_format}
Ensure that the description, status, and key changes implemented are indented one tab more than the PR title line. The PR title should include the exact title from the original list, followed by the PR number in square brackets, which is also a link to the PR.
    """
    
    return summarize_with_gemini(f"{user_prompt}\n{accomplishments}")

    # Uncomment the line below and comment out the line above if you want to use Groq instead of Gemini
    # return summarize_with_groq(f"{user_prompt}\n{accomplishments}")