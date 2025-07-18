"""Date Time Utility Module

This module provides utility functions for formatting dates, times,
and durations in various human-readable formats.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import datetime
from typing import Union, List


def ordinal(n: int) -> str:
    """Convert a number to its ordinal string representation.

    Args:
        n (int): Number to convert

    Returns:
        str: Ordinal representation (e.g., 1st, 2nd, 3rd, 4th)
    """
    return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))


def format_time(dt: datetime) -> str:
    """Format datetime to 12-hour clock format with AM/PM.

    Args:
        dt (datetime): Datetime object to format

    Returns:
        str: Formatted time (e.g., "9:30 AM", "2:45 PM")
    """
    return dt.strftime('%-I:%M %p').lower().replace('am', 'AM').replace('pm', 'PM')


def format_duration(seconds: Union[int, float]) -> str:
    """Format duration in seconds to human-readable string.

    Converts seconds to the most appropriate unit (seconds/minutes/hours) with one decimal place precision.

    Args:
        seconds (Union[int, float]): Duration in seconds

    Returns:
        str: Formatted duration with unit (e.g., "45.0s", "2.5m", "1.5h")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f}m"
    hours = minutes / 60
    return f"{hours:.1f}h"


def format_weekdays_with_dates_for_period(days: List[int], start_date: datetime.date, end_date: datetime.date) -> str:
    """
    Format specified weekdays (by number) with their corresponding dates in a custom period.

    Args:
        days: List of weekdays as integers (1=Monday, ..., 5=Friday)
        start_date: Start date of the period
        end_date: End date of the period

    Returns:
        A formatted string listing the given weekdays with full dates (e.g., "Monday, June 3rd, 2024").
    """
    formatted_days = []
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    # Calculate the Monday of the start date's week
    start_monday = start_date - datetime.timedelta(days=start_date.weekday())
    
    for day in days:
        if 1 <= day <= 5:
            # Calculate the date for this weekday in the period
            date = start_monday + datetime.timedelta(days=day - 1)
            
            # Check if this date falls within our period
            if start_date <= date <= end_date:
                formatted_days.append(f"{day_names[day - 1]}, {date.strftime('%B')} {ordinal(date.day)}, {date.year}")

    return format_bulleted_list(formatted_days, indent="  ")


def format_weekdays_with_dates(days: List[int]) -> str:
    """
    Format specified weekdays (by number) with their corresponding dates in the current week.

    Args:
        days: List of weekdays as integers (1=Monday, ..., 5=Friday)

    Returns:
        A formatted string listing the given weekdays with full dates (e.g., "Monday, June 3rd, 2024").
    """
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=4)  # Friday
    
    return format_weekdays_with_dates_for_period(days, start_of_week, end_of_week)


def get_current_week_period() -> str:
    """
    Get the period from last week's Sunday to this week's Saturday in format 'DD Month YYYY - DD Month YYYY'.

    Returns:
        str: Formatted string, e.g. '04 May 2025 - 10 May 2025'
    """
    import datetime

    today = datetime.date.today()
    this_week_monday = today - datetime.timedelta(days=today.weekday())
    last_week_sunday = this_week_monday - datetime.timedelta(days=1)
    this_week_saturday = this_week_monday + datetime.timedelta(days=5)
    return f"{last_week_sunday.strftime('%d %B %Y')} - {this_week_saturday.strftime('%d %B %Y')}"


def format_bulleted_list(items: List[str], indent: str = "") -> str:
    """Format list items with bullets and optional indentation.

    Args:
        items: List of items to format
        indent: String to prepend for indentation

    Returns:
        Formatted string with bulleted items
    """
    if not items:
        return f"{indent}* None"
    return '\n'.join(f"{indent}* {item}" for item in items)
