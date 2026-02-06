"""
Utility functions and helpers for Personal Finance Manager
"""
from datetime import datetime
from config import DATE_FORMAT, DATETIME_FORMAT, CURRENCY_SYMBOL
import re


def format_currency(amount):
    """Format amount as currency string"""
    return f"{CURRENCY_SYMBOL}{amount:,.2f}"


def format_date(date_obj):
    """Format datetime object to date string"""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime(DATE_FORMAT)


def format_datetime(datetime_obj):
    """Format datetime object to datetime string"""
    if isinstance(datetime_obj, str):
        return datetime_obj
    return datetime_obj.strftime(DATETIME_FORMAT)


def parse_date(date_str):
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str, DATE_FORMAT)
    except:
        return datetime.now()


def parse_datetime(datetime_str):
    """Parse datetime string to datetime object"""
    try:
        return datetime.strptime(datetime_str, DATETIME_FORMAT)
    except:
        return datetime.now()


def validate_amount(amount_str):
    """Validate and parse amount string"""
    try:
        amount = float(amount_str)
        if amount <= 0:
            return None, "Amount must be greater than 0"
        return amount, None
    except ValueError:
        return None, "Invalid amount format"


def validate_date(date_str):
    """Validate date string"""
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True, None
    except ValueError:
        return False, f"Invalid date format. Use {DATE_FORMAT}"


def get_month_year(date_obj):
    """Get month-year string from date"""
    if isinstance(date_obj, str):
        date_obj = parse_date(date_obj)
    return date_obj.strftime("%B %Y")


def get_current_month_range():
    """Get start and end date of current month"""
    now = datetime.now()
    start_date = now.replace(day=1).strftime(DATE_FORMAT)
    
    # Get last day of month
    if now.month == 12:
        next_month = now.replace(year=now.year + 1, month=1, day=1)
    else:
        next_month = now.replace(month=now.month + 1, day=1)
    
    from datetime import timedelta
    last_day = (next_month - timedelta(days=1)).strftime(DATE_FORMAT)
    
    return start_date, last_day


def get_date_range_months(start_date, end_date):
    """Get list of month-year strings between two dates"""
    if isinstance(start_date, str):
        start_date = parse_date(start_date)
    if isinstance(end_date, str):
        end_date = parse_date(end_date)
    
    months = []
    current = start_date
    while current <= end_date:
        months.append(current.strftime("%Y-%m"))
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    return months


def truncate_text(text, max_length=30):
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def get_color_for_percentage(percentage):
    """Get color based on percentage value"""
    from config import COLORS
    if percentage >= 80:
        return COLORS["danger"]
    elif percentage >= 60:
        return COLORS["warning"]
    else:
        return COLORS["success"]


def sanitize_input(text):
    """Sanitize user input to prevent SQL injection"""
    # Remove any potentially harmful characters
    return re.sub(r'[^\w\s\-.,@]', '', text)


def generate_uuid():
    """Generate UUID for transactions"""
    import uuid
    return str(uuid.uuid4())


def get_time_ago(datetime_str):
    """Get human-readable time ago string"""
    if not datetime_str:
        return "Never"
    
    try:
        dt = parse_datetime(datetime_str)
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    except:
        return "Unknown"
