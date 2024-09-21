def ordinal(n):
    return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

def format_time(dt):
    return dt.strftime('%-I:%M %p').lower().replace('am', 'AM').replace('pm', 'PM')