"""
Today Page - Server-side rendering with Python
Moves as much logic as possible from JavaScript to Python.
All data read from SQLite database.
"""
from flask import Blueprint, render_template
from datetime import datetime, date, timedelta
import random

from app.database import (
    get_all_settings, get_week_dates, get_month_start,
    get_python_sessions_by_date, sum_python_hours,
    get_vietnamese_sessions_by_date, sum_vietnamese_minutes,
    get_freelance_income_since,
    get_milestones_upcoming,
    calculate_streak, calculate_streak_with_grace,
)
from app.routes.api import MOTIVATIONS, determine_daily_focus

today_bp = Blueprint('today_page', __name__)


def format_time_from_seconds(total_seconds: int) -> str:
    """Format seconds as HH:MM:SS string."""
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_today_date_formatted() -> str:
    """Get today's date in a nice format."""
    return date.today().strftime('%A, %B %d, %Y')


def calculate_days_remaining() -> int:
    """Calculate days remaining until target date."""
    settings = get_all_settings()
    target_date = datetime.strptime(settings['target_date'], '%Y-%m-%d').date()
    return max(0, (target_date - date.today()).days)


def calculate_days_left_in_month() -> int:
    """Calculate days left in the current month."""
    today = date.today()
    last_day = date(today.year, today.month + 1, 1) - timedelta(days=1) if today.month < 12 else date(today.year, 12, 31)
    return last_day.day - today.day


def get_python_data() -> dict:
    """Get all Python learning data for today page."""
    settings = get_all_settings()
    today_str = date.today().isoformat()
    week_start, week_end = get_week_dates()

    # Today's sessions
    today_sessions = get_python_sessions_by_date(today_str)
    today_hours = sum(s['hours'] for s in today_sessions)

    # Week's hours
    week_hours = sum_python_hours(week_start.isoformat(), week_end.isoformat())

    # Targets
    weekly_target = settings['python_weekly_target']
    daily_target = round(weekly_target / 7, 1)

    # Progress percentages
    daily_progress = min(100, int((today_hours / daily_target) * 100)) if daily_target > 0 else 0
    week_progress = min(100, int((week_hours / weekly_target) * 100)) if weekly_target > 0 else 0

    # Badge info
    if today_hours >= daily_target:
        badge_text = 'Done!'
        badge_class = 'badge-success'
    else:
        badge_text = f"{(daily_target - today_hours):.1f}h left"
        badge_class = 'badge-neutral'

    return {
        'today_hours': round(today_hours, 1),
        'daily_target': daily_target,
        'daily_progress': daily_progress,
        'week_hours': round(week_hours, 1),
        'weekly_target': weekly_target,
        'week_progress': week_progress,
        'today_sessions': today_sessions,
        'badge_text': badge_text,
        'badge_class': badge_class,
    }


def get_vietnamese_data() -> dict:
    """Get all Vietnamese learning data for today page."""
    settings = get_all_settings()
    today_str = date.today().isoformat()
    week_start, week_end = get_week_dates()

    # Today's sessions
    today_sessions = get_vietnamese_sessions_by_date(today_str)
    today_minutes = sum(s['minutes'] for s in today_sessions)

    # Week's minutes
    week_minutes = sum_vietnamese_minutes(week_start.isoformat(), week_end.isoformat())

    # Targets
    weekly_target_hours = settings['vietnamese_weekly_target']
    weekly_target_minutes = weekly_target_hours * 60
    daily_target = int(weekly_target_minutes / 7)

    # Progress percentages
    daily_progress = min(100, int((today_minutes / daily_target) * 100)) if daily_target > 0 else 0
    week_progress = min(100, int((week_minutes / weekly_target_minutes) * 100)) if weekly_target_minutes > 0 else 0

    # Streak
    streak = calculate_streak()

    # Badge info
    if today_minutes >= daily_target:
        badge_text = 'Done!'
        badge_class = 'badge-success'
    else:
        badge_text = f"{daily_target - today_minutes}m left"
        badge_class = 'badge-neutral'

    return {
        'today_minutes': today_minutes,
        'daily_target': daily_target,
        'daily_progress': daily_progress,
        'week_minutes': week_minutes,
        'week_hours': round(week_minutes / 60, 1),
        'weekly_target_hours': weekly_target_hours,
        'week_progress': week_progress,
        'today_sessions': today_sessions,
        'streak': streak,
        'badge_text': badge_text,
        'badge_class': badge_class,
    }


def get_income_data() -> dict:
    """Get income/freelance data for today page."""
    settings = get_all_settings()
    month_start = get_month_start()

    income_this_month = get_freelance_income_since(month_start.isoformat())
    income_target = settings['income_target']
    income_gap = max(0, income_target - income_this_month)
    income_progress = min(100, int((income_this_month / income_target) * 100)) if income_target > 0 else 0

    circumference = 339.292
    ring_offset = circumference - (income_progress / 100) * circumference

    return {
        'this_month': income_this_month,
        'target': income_target,
        'gap': income_gap,
        'progress': income_progress,
        'ring_offset': ring_offset,
        'days_left': calculate_days_left_in_month(),
    }


def get_smart_focus() -> dict:
    """Get smart focus recommendation."""
    settings = get_all_settings()
    week_start, week_end = get_week_dates()
    month_start = get_month_start()

    py_week = sum_python_hours(week_start.isoformat(), week_end.isoformat())
    vn_week_mins = sum_vietnamese_minutes(week_start.isoformat(), week_end.isoformat())
    vn_week = vn_week_mins / 60

    py_target = settings['python_weekly_target']
    vn_target = settings['vietnamese_weekly_target']

    py_percent = min(100, int((py_week / py_target) * 100)) if py_target > 0 else 100
    vn_percent = min(100, int((vn_week / vn_target) * 100)) if vn_target > 0 else 100

    income_month = get_freelance_income_since(month_start.isoformat())
    income_target = settings['income_target']
    income_percent = min(100, int((income_month / income_target) * 100)) if income_target > 0 else 100

    streak_info = calculate_streak_with_grace()
    return determine_daily_focus(py_percent, vn_percent, income_percent, streak_info)


def get_upcoming_milestones() -> list:
    """Get milestones coming up this week."""
    _, week_end = get_week_dates()
    upcoming = get_milestones_upcoming(week_end.isoformat())

    for m in upcoming:
        dt = datetime.strptime(m['target_date'], '%Y-%m-%d')
        m['day'] = dt.day
        m['month_short'] = dt.strftime('%b')

    return upcoming


def should_show_evening_reflection() -> bool:
    """Check if it's evening (after 6 PM)."""
    return datetime.now().hour >= 18


def format_currency(amount_ron: float, currency_code: str = None) -> str:
    """Format amount from RON to preferred currency."""
    settings = get_all_settings()
    currency_code = currency_code or settings.get('preferred_currency', 'EUR')
    rates = settings.get('exchange_rates', {'EUR': 4.97, 'USD': 4.55, 'VND': 0.00018})

    if currency_code == 'RON':
        return f"{amount_ron:,.0f} RON"

    rate = rates.get(currency_code, 1)
    converted = amount_ron / rate

    symbols = {'EUR': '\u20ac', 'USD': '$', 'VND': '\u20ab'}
    symbol = symbols.get(currency_code, currency_code)

    if currency_code == 'VND':
        return f"{converted:,.0f} {symbol}"
    return f"{symbol}{converted:,.0f}"


@today_bp.route('/today')
def today_page():
    """Render the today page with all data calculated server-side."""
    context = {
        'today_date': get_today_date_formatted(),
        'days_remaining': calculate_days_remaining(),
        'motivation': random.choice(MOTIVATIONS),
        'python': get_python_data(),
        'vietnamese': get_vietnamese_data(),
        'income': get_income_data(),
        'focus': get_smart_focus(),
        'milestones': get_upcoming_milestones(),
        'show_reflection': should_show_evening_reflection(),
        'format_currency': format_currency,
    }

    return render_template('hanoi-relocation/today.html', **context)
