# LLM Prompts

This directory contains the prompt templates used by the LLM services to generate weekly reports.

## Files

- `system_prompt.md`: Contains the system prompt that instructs the LLM on its role and expected behavior
- `user_prompt.md`: Contains the template for the user prompt with formatting instructions and rules for summarizing PRs

## Usage

These prompts are used in the `core/services/llm_service.py` module to generate formatted summaries of pull requests and commit messages using Google Gemini and Groq LLM models.

When using these prompts in code, the `{content}` placeholder in the user prompt will be replaced with the actual PR data to be summarized. 

## How-to

Create the file with the specified name above and update the prompt content as needed. The prompt will be automatically loaded by the program during execution.