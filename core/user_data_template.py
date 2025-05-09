"""User Data Module

This module contains user-specific data for weekly report generation including
work information, learning activities, next steps, and email template.

Please copy this file and rename it as user_data.py to make it configurable for you.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
    - Glenn Steven Santoso (glenn.s.santoso@gdplabs.id)
"""

ISSUES: list = []

# We really hope these stay at 0...
MAJOR_BUGS_CURRENT_MONTH: int = 0
MINOR_BUGS_CURRENT_MONTH: int = 0

MAJOR_BUGS_HALF_YEAR: int = 0
MINOR_BUGS_HALF_YEAR: int = 0

"""Work from office days, using numbers 1-5 representing Monday to Friday.
Example: [1, 2, 5] means WFO on Monday, Tuesday, and Friday"""
WFO_DAYS: list[int] = [1, 2, 5]

"""Self accomplishments for the week, in case accomplishments are not available from GitHub and is needed to be written manually"""
OTHER_ACCOMPLISHMENTS: list[str] = [
    "Your self accomplishment 1",
    "Your self accomplishment 2",
    "Your self accomplishment 3",
]

"""Since each teams has their own OMTM/Metrics and not all of them can be automated, therefore an option to fill it manually is provided"""
OMTM: list[str] = [
    "Your OMTM 1",
    "Your OMTM 2",
    "Your OMTM 3",
]

"""Out of office days, using numbers 1-5 representing Monday to Friday.
Example: [1, 2, 5] means WFO on Monday, Tuesday, and Friday"""
OUT_OF_OFFICE_DAYS: list[int] = []

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
    "[O'Reilly Media] [Clean Architecture: A Craftsman's Guide to Software Structure and Design](https://www.oreilly.com/library/view/clean-architecture-a/9780134494272/) by Robert C. Martin (Chapter 26/34)",
]
