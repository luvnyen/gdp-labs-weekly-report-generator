"""LLM Service Module

This module provides functionality to interact with Google Gemini and Groq
for summarizing pull requests and commit messages.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
    - Mikhael Chris (mikhael.chris@gdplabs.id)
"""

import os
import re

import google.generativeai as genai
from groq import Groq

from config.config import GOOGLE_GEMINI_API_KEY, GROQ_API_KEY


def load_prompt(filename: str) -> str:
    """Load prompt content from a markdown file.

    Args:
        filename (str): Name of the markdown file in the prompts directory

    Returns:
        str: Content of the prompt file
    """
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    prompt_path = os.path.join(project_root, "prompts", filename)

    with open(prompt_path, "r") as file:
        return file.read()


def load_prompt_or_fail(filename: str) -> str:
    """Load prompt content from a markdown file.

    Args:
        filename (str): Name of the markdown file in the prompts directory

    Returns:
        str: Content of the prompt file
    """
    try:
        return load_prompt(filename)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Prompt file {filename} not found. Please create a `{filename}` file in the `prompts` directory."
        )


USER_PROMPT = load_prompt_or_fail("user_prompt.md")
SYSTEM_PROMPT = load_prompt_or_fail("system_prompt.md")


def clean_response(response: str) -> str:
    """Clean up the response by removing the thinking process and unwanted headers.

    Args:
        response (str): Raw response to be cleaned.

    Returns:
        str: Cleaned response containing only the formatted summaries.
    """
    # Remove a thinking process section
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)

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
            },
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
