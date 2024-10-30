"""Date Time Utility Module

This module provides utility functions for formatting dates, times,
and durations in various human-readable formats.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

from datetime import datetime
from typing import Union


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
