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