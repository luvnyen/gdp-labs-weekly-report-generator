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

SHARED_PROMPT_TEMPLATE = """Format each PR exactly as shown below, without any additional headers or prefixes:

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
   - List a maximum of 7 most important bullet points
   - If there are more than 7 changes, summarize the main themes into 7 or fewer points
   - Ensure each bullet point is concise but informative
   - No sub-bullet points allowed
5. Format all code-related terms with backticks (e.g., `className`)
6. If no commit details exist, use PR title for both Description and Key Changes
7. Start each PR directly with * - no section headers, PR numbers, or other prefixes

Here are the PRs to summarize:
{content}"""

GEMINI_PROMPT_TEMPLATE = SHARED_PROMPT_TEMPLATE

GROQ_SYSTEM_PROMPT = """You are a technical writer specializing in summarizing pull requests and commit messages.
Provide only the formatted output following the exact structure specified in the user's prompt.
Do not include any explanations, thinking process, or additional headers."""

GROQ_USER_PROMPT = SHARED_PROMPT_TEMPLATE

def clean_groq_response(response: str) -> str:
    """Clean up Groq's response by removing a thinking process and unwanted headers.

    Args:
        response (str): Raw response from Groq API

    Returns:
        str: Cleaned response containing only the formatted PR summaries
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
        model="deepseek-r1-distill-llama-70b",
    )

    return clean_groq_response(chat_completion.choices[0].message.content)


def summarize_with_gemini(content: str) -> str:
    """Summarize pull requests using Google's Gemini model.

    Args:
        content (str): Raw PR and commit content to summarize

    Returns:
        str: Formatted markdown summary from Gemini
    """
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    formatted_prompt = GEMINI_PROMPT_TEMPLATE.format(content=content)
    response = model.generate_content(formatted_prompt)

    return response.text