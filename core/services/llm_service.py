"""LLM Service Module

This module provides functionality to interact with Google Gemini
for summarizing pull requests and commit messages.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import google.generativeai as genai

from config.config import GOOGLE_GEMINI_API_KEY

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

Here are the PRs you need to summarize:
{content}"""


def summarize_with_gemini(content: str) -> str:
    """Summarize pull requests using Google's Gemini model.

    Args:
        content (str): Raw PR and commit content to summarize

    Returns:
        str: Formatted markdown summary from Gemini
    """
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    formatted_prompt = GEMINI_PROMPT_TEMPLATE.format(content=content)
    response = model.generate_content(formatted_prompt)

    return response.text
