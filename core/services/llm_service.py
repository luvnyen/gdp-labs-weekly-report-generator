"""LLM Service Module

This module provides functionality to interact with Google Gemini and Groq
for summarizing pull requests and commit messages.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import re

import google.generativeai as genai
from groq import Groq

from config.config import GROQ_API_KEY, GOOGLE_GEMINI_API_KEY

SYSTEM_PROMPT = """You are a technical writer specializing in summarizing pull requests and commit messages.
Provide only the formatted output following the exact structure specified in the user's prompt.
Do not include any explanations, thinking process, or additional headers."""

USER_PROMPT = """Format each PR exactly as shown below, without any additional headers or prefixes:

* test(core): increase code coverage for `/core/personnel/api/v1` module [CATAPA-API#18420](https://github.com/GDP-ADMIN/CATAPA-API/pull/18420)
    * **Description:** Enhanced test coverage through improved MSS integration, notification services, and null handling implementations.
    * **Status:** leave_this_blank
    * **Key Changes Implemented:**
        * Enhanced `MssEmployeeApiController` with `Optional`
        * Simplified notification config services using `map()`
        * Updated tests for better null handling and mocking

Rules for summarizing:
1. Format the PR title exactly as shown in the example, including the PR number and link
2. Description must be a single sentence summary of the key changes
3. Status must always be exactly "leave_this_blank"
4. For Key Changes Implemented:
   - Extract and list ALL significant changes from commits, aim for at least 5-8 bullet points per PR
   - Focus on technical implementation details, method changes, and code improvements
   - Be specific about what was added, modified, or enhanced
   - Include class names, methods, and technical approaches used
   - Always format code elements with backticks (e.g., `className`)
   - No sub-bullet points allowed
5. If no commit details exist, use PR title for both Description and Key Changes
6. Start each PR directly with * - no section headers, PR numbers, or other prefixes
7. Prioritize extracting comprehensive implementation details over brevity

Here are the PRs to summarize:
{content}"""

def clean_response(response: str) -> str:
    """Clean up the response by removing the thinking process and unwanted headers.

    Args:
        response (str): Raw response to be cleaned.

    Returns:
        str: Cleaned response containing only the formatted summaries.
    """
    # Remove a thinking process section
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)

    return response.strip()

def summarize_with_groq(content: str) -> str:
    """Summarize pull requests using Groq's LLM model.

    This function takes raw PR and commit content and generates a formatted Markdown summary
    using the Groq API with the deepseek-r1-distill-llama-70b model. The summary follows
    a specific format including PR title, description, status, and key changes implemented.

    Args:
        content (str): Raw PR and commit content to summarize. It should contain PR titles,
                      numbers, and associated commit messages.

    Returns:
        str: Formatted markdown summary containing structured information about each PR,
             including titles, descriptions, and key changes.
    """
    client = Groq(api_key=GROQ_API_KEY)

    formatted_user_prompt = USER_PROMPT.format(content=content)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": formatted_user_prompt,
            }
        ],
        model="deepseek-r1-distill-llama-70b",
    )

    return clean_response(chat_completion.choices[0].message.content)

def summarize_with_gemini(content: str) -> str:
    """Summarize pull requests using Google's Gemini model.

    Args:
        content (str): Raw PR and commit content to summarize

    Returns:
        str: Formatted Markdown summary from Gemini
    """
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")

    formatted_prompt = SYSTEM_PROMPT + USER_PROMPT.format(content=content)
    response = model.generate_content(formatted_prompt)

    return response.text
