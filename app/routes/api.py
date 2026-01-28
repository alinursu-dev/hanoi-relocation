"""
API Routes - SQLite persistent storage
All data is stored in hanoi.db and persists across server restarts.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
import random

from app.database import (
    get_all_settings, update_settings as db_update_settings,
    get_vietnamese_sessions, get_vietnamese_sessions_by_date,
    get_vietnamese_sessions_between, sum_vietnamese_minutes,
    create_vietnamese_session, delete_vietnamese_session,
    get_python_sessions, get_python_sessions_by_date,
    get_python_sessions_between, sum_python_hours,
    create_python_session, delete_python_session,
    get_freelance_projects, get_freelance_income_since, get_freelance_stats,
    create_freelance_project, delete_freelance_project,
    get_milestones, get_milestones_upcoming,
    create_milestone, update_milestone, delete_milestone,
    get_notes, create_note, update_note, delete_note,
    get_learning_path, update_learning_skill,
    calculate_streak, calculate_streak_with_grace,
    get_week_dates, get_month_start,
    get_vietnamese_session_dates,
)

api_bp = Blueprint('api', __name__)

MOTIVATIONS = [
    "Every day is a step closer to Hanoi. Keep pushing!",
    "Progress, not perfection. You're doing great!",
    "Small consistent steps lead to big changes.",
    "Your future self will thank you for today's effort.",
    "The best time to start was yesterday. The next best time is now.",
    "Believe in yourself. You've got this!",
    "One day at a time. One step at a time.",
    "Your dedication will pay off. Stay focused!",
    "Dream big, work hard, stay focused.",
    "Every expert was once a beginner. Keep learning!"
]


# ============ HELPER FUNCTIONS ============

def determine_daily_focus(py_percent, vn_percent, income_percent, streak_info):
    """Determine what the user should focus on today."""
    suggestions = {
        'python': [
            "Work through a Python tutorial or course module",
            "Practice coding challenges on LeetCode or HackerRank",
            "Build a small project to apply what you've learned"
        ],
        'vietnamese': [
            "Complete a Duolingo lesson",
            "Listen to a VietnamesePod101 episode",
            "Practice speaking with a tutor on italki"
        ],
        'freelance': [
            "Browse Upwork for new opportunities",
            "Update your portfolio or profile",
            "Reach out to past clients for referrals"
        ],
        'balanced': [
            "Great job staying on track!",
            "Consider working on your portfolio",
            "Take time to review and consolidate learning"
        ]
    }

    # Priority 1: Protect the streak
    if streak_info['at_risk'] and not streak_info['practiced_today']:
        today_str = date.today().isoformat()
        mins_today = sum_vietnamese_minutes(today_str, today_str)
        needed = max(15, 60 - mins_today)
        return {
            'area': 'vietnamese',
            'priority': 'urgent',
            'reason': f"Your {streak_info['streak']}-day streak is at risk!",
            'suggestion': f"Just {needed} more minutes to keep it alive",
            'icon': '🔥'
        }

    # Priority 2: Catch up on the most behind area
    if vn_percent < py_percent and vn_percent < 70:
        return {
            'area': 'vietnamese',
            'priority': 'high',
            'reason': f"You're at {vn_percent}% of your Vietnamese target (vs {py_percent}% Python)",
            'suggestion': random.choice(suggestions['vietnamese']),
            'icon': '🇻🇳'
        }

    if py_percent < vn_percent and py_percent < 70:
        return {
            'area': 'python',
            'priority': 'high',
            'reason': f"You're at {py_percent}% of your Python target (vs {vn_percent}% Vietnamese)",
            'suggestion': random.choice(suggestions['python']),
            'icon': '🐍'
        }

    # Priority 3: Both learning areas good, focus on income
    if py_percent >= 70 and vn_percent >= 70 and income_percent < 50:
        return {
            'area': 'freelance',
            'priority': 'medium',
            'reason': f"Learning is on track! Income is at {income_percent}% of target",
            'suggestion': random.choice(suggestions['freelance']),
            'icon': '💼'
        }

    # Priority 4: Everything on track
    if py_percent >= 80 and vn_percent >= 80:
        return {
            'area': 'balanced',
            'priority': 'low',
            'reason': "You're crushing it this week!",
            'suggestion': random.choice(suggestions['balanced']),
            'icon': '🎯'
        }

    # Default: work on the lower one
    if py_percent <= vn_percent:
        return {
            'area': 'python',
            'priority': 'medium',
            'reason': f"Python is at {py_percent}% - room for improvement",
            'suggestion': random.choice(suggestions['python']),
            'icon': '🐍'
        }
    else:
        return {
            'area': 'vietnamese',
            'priority': 'medium',
            'reason': f"Vietnamese is at {vn_percent}% - room for improvement",
            'suggestion': random.choice(suggestions['vietnamese']),
            'icon': '🇻🇳'
        }


def get_recommendations():
    """Get smart recommendations based on current progress."""
    settings = get_all_settings()
    today = date.today()
    target_date = datetime.strptime(settings['target_date'], '%Y-%m-%d').date()
    week_start, week_end = get_week_dates()
    month_start = get_month_start()

    # Calculate weekly progress
    py_week = sum_python_hours(week_start.isoformat(), week_end.isoformat())
    vn_week_mins = sum_vietnamese_minutes(week_start.isoformat(), week_end.isoformat())
    vn_week = vn_week_mins / 60

    py_target = settings['python_weekly_target']
    vn_target = settings['vietnamese_weekly_target']

    py_percent = min(100, int((py_week / py_target) * 100)) if py_target > 0 else 100
    vn_percent = min(100, int((vn_week / vn_target) * 100)) if vn_target > 0 else 100

    # Income progress
    income_month = get_freelance_income_since(month_start.isoformat())
    income_target = settings['income_target']
    income_percent = min(100, int((income_month / income_target) * 100)) if income_target > 0 else 100

    # Streak with grace period
    streak_info = calculate_streak_with_grace()

    # Calculate pace for Vietnamese (600 hours to B1)
    vn_total_hours = sum_vietnamese_minutes() / 60
    hours_remaining = max(0, 600 - vn_total_hours)
    weeks_remaining = max(1, (target_date - today).days / 7)
    required_weekly = round(hours_remaining / weeks_remaining, 1)

    # Determine daily focus
    focus = determine_daily_focus(py_percent, vn_percent, income_percent, streak_info)

    # Calculate weekly grade
    avg_percent = (py_percent + vn_percent + income_percent) / 3
    if avg_percent >= 90:
        grade = 'A'
    elif avg_percent >= 75:
        grade = 'B'
    elif avg_percent >= 60:
        grade = 'C'
    else:
        grade = 'D'

    # Goal adjustment suggestion
    adjustment = None
    if py_percent < 50 and vn_percent < 50:
        suggested_py = max(4, int(py_target * 0.7))
        suggested_vn = max(4, int(vn_target * 0.7))
        adjustment = {
            'needed': True,
            'message': f"Consider adjusting targets: Python to {suggested_py}h/week, Vietnamese to {suggested_vn}h/week",
            'suggested_python': suggested_py,
            'suggested_vietnamese': suggested_vn
        }

    return jsonify({
        'daily_focus': focus,
        'pace': {
            'vietnamese_total_hours': round(vn_total_hours, 1),
            'vietnamese_remaining_hours': round(hours_remaining, 1),
            'vietnamese_required_weekly': required_weekly,
            'vietnamese_current_target': vn_target,
            'on_track': required_weekly <= vn_target,
            'weeks_remaining': int(weeks_remaining)
        },
        'streak': {
            'current': streak_info['streak'],
            'at_risk': streak_info['at_risk'],
            'grace_active': streak_info['grace_active'],
            'practiced_today': streak_info['practiced_today']
        },
        'weekly_summary': {
            'python_hours': round(py_week, 1),
            'python_target': py_target,
            'python_percent': py_percent,
            'vietnamese_hours': round(vn_week, 1),
            'vietnamese_target': vn_target,
            'vietnamese_percent': vn_percent,
            'income_current': income_month,
            'income_target': income_target,
            'income_percent': income_percent,
            'grade': grade
        },
        'adjustment': adjustment
    })


# ============ AUTH ENDPOINTS ============

@api_bp.route('/auth.php', methods=['GET', 'POST'])
def auth():
    """Mock auth endpoint - always returns authenticated for prototype."""
    action = request.args.get('action')

    if action == 'check':
        return jsonify({
            'authenticated': True,
            'user': {'id': 1, 'email': 'demo@example.com'}
        })
    elif action == 'login':
        return jsonify({
            'success': True,
            'user': {'id': 1, 'email': 'demo@example.com'}
        })
    elif action == 'logout':
        return jsonify({'success': True})
    elif action == 'register':
        return jsonify({
            'success': True,
            'user': {'id': 1, 'email': 'demo@example.com'}
        })

    return jsonify({'authenticated': True})


# ============ DASHBOARD ENDPOINTS ============

@api_bp.route('/dashboard.php', methods=['GET', 'PUT', 'POST', 'DELETE'])
def dashboard():
    """Main dashboard API endpoint."""
    action = request.args.get('action')

    if action == 'get_all':
        return get_all()
    elif action == 'stats':
        return get_stats()
    elif action == 'today':
        return get_today()
    elif action == 'settings':
        if request.method == 'PUT':
            return handle_update_settings()
        return handle_get_settings()
    elif action == 'milestones':
        return handle_milestones()
    elif action == 'python':
        return handle_python()
    elif action == 'vietnamese':
        return handle_vietnamese()
    elif action == 'freelance':
        return handle_freelance()
    elif action == 'notes':
        return handle_notes()
    elif action == 'learning_path':
        return handle_learning_path()
    elif action == 'recommendations':
        return get_recommendations()

    return jsonify({'error': 'Invalid action'}), 400


def get_all():
    """Get all dashboard data."""
    return jsonify({
        'vietnameseSessions': get_vietnamese_sessions(),
        'pythonSessions': get_python_sessions(),
        'freelanceProjects': get_freelance_projects(),
        'milestones': get_milestones(),
        'notes': get_notes()
    })


def get_stats():
    """Get dashboard statistics."""
    settings = get_all_settings()
    today = date.today()
    target_date = datetime.strptime(settings['target_date'], '%Y-%m-%d').date()
    week_start, week_end = get_week_dates()
    month_start = get_month_start()

    # Vietnamese stats
    vn_total = sum_vietnamese_minutes()
    vn_week = sum_vietnamese_minutes(week_start.isoformat(), week_end.isoformat())

    # Python stats
    py_total = sum_python_hours()
    py_week = sum_python_hours(week_start.isoformat(), week_end.isoformat())

    # Freelance stats
    fl_stats = get_freelance_stats()
    fl_month = get_freelance_income_since(month_start.isoformat())
    avg_rate = fl_stats['total_income'] / fl_stats['total_hours'] if fl_stats['total_hours'] > 0 else 0

    # Learning path
    lp = get_learning_path()
    completed_skills = sum(1 for s in lp if s['completed'])
    total_skills = len(lp)
    lp_percentage = int((completed_skills / total_skills) * 100) if total_skills > 0 else 0

    # Financial
    runway = int(settings['savings'] / settings['monthly_burn']) if settings['monthly_burn'] > 0 else 0

    return jsonify({
        'timeline': {
            'daysRemaining': max(0, (target_date - today).days),
            'targetDate': settings['target_date']
        },
        'vietnamese': {
            'totalMinutes': vn_total,
            'totalHours': round(vn_total / 60, 1),
            'thisWeek': round(vn_week / 60, 1),
            'weeklyTarget': settings['vietnamese_weekly_target'],
            'streak': calculate_streak()
        },
        'python': {
            'totalHours': round(py_total, 1),
            'thisWeek': round(py_week, 1),
            'weeklyTarget': settings['python_weekly_target']
        },
        'freelance': {
            'incomeTotal': fl_stats['total_income'],
            'incomeThisMonth': fl_month,
            'incomeTarget': settings['income_target'],
            'totalProjects': fl_stats['total_projects'],
            'avgHourlyRate': round(avg_rate, 2)
        },
        'financial': {
            'savings': settings['savings'],
            'monthlyBurn': settings['monthly_burn'],
            'runway': runway
        },
        'learningPath': {
            'completed': completed_skills,
            'total': total_skills,
            'percentage': lp_percentage
        }
    })


def get_today():
    """Get today's focused data."""
    settings = get_all_settings()
    today = date.today()
    today_str = today.isoformat()
    target_date = datetime.strptime(settings['target_date'], '%Y-%m-%d').date()
    week_start, week_end = get_week_dates()
    month_start = get_month_start()

    # Python today/week
    py_today = get_python_sessions_by_date(today_str)
    py_today_hours = sum(s['hours'] for s in py_today)
    py_week = sum_python_hours(week_start.isoformat(), week_end.isoformat())

    # Vietnamese today/week
    vn_today = get_vietnamese_sessions_by_date(today_str)
    vn_today_mins = sum(s['minutes'] for s in vn_today)
    vn_week = sum_vietnamese_minutes(week_start.isoformat(), week_end.isoformat())

    # Income
    income_month = get_freelance_income_since(month_start.isoformat())
    income_gap = max(0, settings['income_target'] - income_month)
    income_progress = min(100, int((income_month / settings['income_target']) * 100)) if settings['income_target'] > 0 else 0

    # Upcoming milestones
    upcoming = get_milestones_upcoming(week_end.isoformat())

    # Daily targets
    py_daily = round(settings['python_weekly_target'] / 7, 1)
    vn_daily = int((settings['vietnamese_weekly_target'] * 60) / 7)

    return jsonify({
        'daysRemaining': max(0, (target_date - today).days),
        'motivation': random.choice(MOTIVATIONS),
        'python': {
            'todayHours': round(py_today_hours, 1),
            'dailyTarget': py_daily,
            'weekHours': round(py_week, 1),
            'weeklyTarget': settings['python_weekly_target'],
            'weekProgress': min(100, int((py_week / settings['python_weekly_target']) * 100)) if settings['python_weekly_target'] > 0 else 0,
            'todaySessions': py_today
        },
        'vietnamese': {
            'todayMinutes': vn_today_mins,
            'dailyTarget': vn_daily,
            'weekMinutes': vn_week,
            'weeklyTarget': settings['vietnamese_weekly_target'] * 60,
            'weekProgress': min(100, int((vn_week / (settings['vietnamese_weekly_target'] * 60)) * 100)) if settings['vietnamese_weekly_target'] > 0 else 0,
            'streak': calculate_streak(),
            'todaySessions': vn_today
        },
        'income': {
            'thisMonth': income_month,
            'target': settings['income_target'],
            'gap': income_gap,
            'progress': income_progress
        },
        'upcomingMilestones': upcoming
    })


def handle_get_settings():
    """Get settings."""
    return jsonify(get_all_settings())


def handle_update_settings():
    """Update settings."""
    data = request.get_json()
    db_update_settings(data)
    return jsonify({'success': True})


def handle_milestones():
    """Handle milestone CRUD."""
    if request.method == 'POST':
        data = request.get_json()
        new_id = create_milestone(
            title=data['title'],
            target_date=data['target_date'],
            category=data.get('category', ''),
            notes=data.get('notes', '')
        )
        return jsonify({'success': True, 'id': new_id})

    elif request.method == 'PUT':
        milestone_id = int(request.args.get('id'))
        data = request.get_json()
        update_milestone(milestone_id, data)
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        milestone_id = int(request.args.get('id'))
        delete_milestone(milestone_id)
        return jsonify({'success': True})

    return jsonify(get_milestones())


def handle_python():
    """Handle Python session CRUD."""
    if request.method == 'POST':
        data = request.get_json()
        new_id = create_python_session(
            session_date=data['session_date'],
            hours=data['hours'],
            topic=data.get('topic', ''),
            notes=data.get('notes', '')
        )
        return jsonify({'success': True, 'id': new_id})

    elif request.method == 'DELETE':
        session_id = int(request.args.get('id'))
        delete_python_session(session_id)
        return jsonify({'success': True})

    return jsonify(get_python_sessions())


def handle_vietnamese():
    """Handle Vietnamese session CRUD."""
    if request.method == 'POST':
        data = request.get_json()
        new_id = create_vietnamese_session(
            session_date=data['session_date'],
            minutes=data['minutes'],
            session_type=data.get('session_type', ''),
            focus_area=data.get('focus_area', '')
        )
        return jsonify({'success': True, 'id': new_id})

    elif request.method == 'DELETE':
        session_id = int(request.args.get('id'))
        delete_vietnamese_session(session_id)
        return jsonify({'success': True})

    return jsonify(get_vietnamese_sessions())


def handle_freelance():
    """Handle freelance project CRUD."""
    if request.method == 'POST':
        data = request.get_json()
        new_id = create_freelance_project(
            title=data['title'],
            project_date=data['project_date'],
            amount=data['amount'],
            hours=data.get('hours', 0),
            platform=data.get('platform', ''),
            description=data.get('description', '')
        )
        return jsonify({'success': True, 'id': new_id})

    elif request.method == 'DELETE':
        project_id = int(request.args.get('id'))
        delete_freelance_project(project_id)
        return jsonify({'success': True})

    return jsonify(get_freelance_projects())


def handle_notes():
    """Handle notes CRUD."""
    if request.method == 'POST':
        data = request.get_json()
        new_id = create_note(
            title=data['title'],
            category=data.get('category', ''),
            content=data.get('content', '')
        )
        return jsonify({'success': True, 'id': new_id})

    elif request.method == 'PUT':
        note_id = int(request.args.get('id'))
        data = request.get_json()
        update_note(note_id, data)
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        note_id = int(request.args.get('id'))
        delete_note(note_id)
        return jsonify({'success': True})

    return jsonify(get_notes())


def handle_learning_path():
    """Handle learning path."""
    if request.method == 'PUT':
        data = request.get_json()
        update_learning_skill(
            skill_id=data.get('skill_id'),
            completed=data.get('completed'),
            project_url=data.get('project_url')
        )
        return jsonify({'success': True})

    return jsonify(get_learning_path())


# ============ CURRENCY ENDPOINT ============

@api_bp.route('/currency.php', methods=['GET', 'PUT'])
def currency():
    """Currency API endpoint."""
    action = request.args.get('action')
    settings = get_all_settings()
    rates = settings.get('exchange_rates', {
        'EUR': 4.97,
        'USD': 4.55,
        'VND': 0.00018
    })

    if action == 'rates':
        if request.method == 'PUT':
            data = request.get_json()
            if data and 'rates' in data:
                new_rates = {}
                for currency_code, rate in data['rates'].items():
                    if currency_code in ['EUR', 'USD', 'VND']:
                        new_rates[currency_code] = float(rate)
                db_update_settings({'exchange_rates': new_rates})
                updated = get_all_settings()
                return jsonify({
                    'success': True,
                    'rates': updated['exchange_rates'],
                    'date': date.today().isoformat()
                })
            return jsonify({'error': 'Invalid rates data'}), 400

        return jsonify({
            'rates': rates,
            'date': date.today().isoformat()
        })

    elif action == 'convert':
        from_curr = request.args.get('from', 'RON')
        to_curr = request.args.get('to', 'EUR')
        amount = float(request.args.get('amount', 0))

        from_rate = rates.get(from_curr, 1) if from_curr != 'RON' else 1
        to_rate = rates.get(to_curr, 1) if to_curr != 'RON' else 1

        amount_in_ron = amount * from_rate
        result = amount_in_ron / to_rate

        return jsonify({
            'from': from_curr,
            'to': to_curr,
            'amount': amount,
            'result': round(result, 2)
        })

    return jsonify({'error': 'Invalid action'}), 400
