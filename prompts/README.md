# LLM Prompts

This directory contains the prompt templates used by the LLM services to generate weekly reports.

## Files

- [`system_prompt.md`](https://github.com/luvnyen/gdp-labs-weekly-report-generator/blob/master/prompts/system_prompt.md): Contains the system prompt that instructs the LLM on its role and expected behavior
- [`user_prompt.md`](https://github.com/luvnyen/gdp-labs-weekly-report-generator/blob/master/prompts/user_prompt.md): Contains the template for the user prompt with formatting instructions and rules for summarizing PRs

## Usage

These prompts are used in the [`core/services/llm_service.py`](https://github.com/luvnyen/gdp-labs-weekly-report-generator/blob/master/core/services/llm_service.py) module to generate formatted summaries of pull requests and commit messages using Google Gemini or Groq LLM.

When using these prompts in code, the `{content}` placeholder in the user prompt will be replaced with the actual PR data to be summarized. 

## How-to

To customize the prompt used by the Weekly Report Agent's LLM service, edit the corresponding file as indicated above. The prompt file is automatically loaded by the application at runtime. By default, a template prompt is provided, but users are encouraged to modify it as needed. When editing `user_prompt.md`, ensure that the `{content}` placeholder remains intact, as it will be dynamically replaced with the PR data to be summarized in the weekly report.

## Default Prompt

### System Prompt
```
You are a technical writer specializing in summarizing pull requests and commit messages.
Provide only the formatted output following the exact structure specified in the user's prompt.
Do not include any explanations, thinking process, or additional headers.
```

### User Prompt
```
Format each PR exactly as shown below, without any additional headers or prefixes:

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
8. Group PRs by repository, using the repository name (with underscores/hyphens replaced by spaces and first letter of each word capitalized) as a heading 3 section header

Here are the PRs to summarize:
{content}
```