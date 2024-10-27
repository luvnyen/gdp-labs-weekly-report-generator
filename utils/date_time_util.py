"""Date Time Utility Module

This module provides utility functions for formatting dates, times,
and durations in various human-readable formats.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

def ordinal(n):
    return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

def format_time(dt):
    return dt.strftime('%-I:%M %p').lower().replace('am', 'AM').replace('pm', 'PM')

def format_duration(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f}m"
    hours = minutes / 60
    return f"{hours:.1f}h"