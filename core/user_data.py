"""User Data Module

This module contains user-specific data for weekly report generation including
work information, learning activities, next steps, and email template.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

ISSUES: list = []

MAJOR_BUGS_CURRENT_MONTH: int = 0
MINOR_BUGS_CURRENT_MONTH: int = 0

MAJOR_BUGS_HALF_YEAR: int = 0
MINOR_BUGS_HALF_YEAR: int = 0

"""Work from office days, using numbers 1-5 representing Monday to Friday.
Example: [1, 2, 5] means WFO on Monday, Tuesday, and Friday"""
WFO_DAYS: list[int] = [1, 2, 5]

NEXT_STEPS = [
    "Next step 1",
]

"""Learning activities format with URL to a specific article, video, or book:
- [title](url) by Author

Examples:
- [Head First Design Patterns, 2nd Edition](https://learning.oreilly.com/library/view/head-first-design/9781492077992/) by Eric Freeman & Elisabeth Robson (Chapter 3/13)
- [Article Title](https://example.com)
- [Video Title](https://youtube.com/watch?v=123)
"""
LEARNING = [
    "[Introducing computer use, a new Claude 3.5 Sonnet, and Claude 3.5 Haiku](https://www.anthropic.com/news/3-5-models-and-computer-use)",
]
