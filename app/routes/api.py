"""
API Routes - In-memory data storage for prototype
All data is stored in memory and resets when the server restarts.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
import random

api_bp = Blueprint('api', __name__)

# ============ IN-MEMORY DATA STORE ============

# Default settings
DATA = {
    'settings': {
        'target_date': '2026-10-31',
        'income_target': 7500,  # RON
        'python_weekly_target': 8,
        'vietnamese_weekly_target': 7,
        'savings': 27500,  # RON
        'monthly_burn': 3000,  # RON
        'preferred_currency': 'EUR',
        'github_username': '',
        # Custom exchange rates (1 unit = X RON)
        'exchange_rates': {
            'EUR': 4.97,
            'USD': 4.55,
            'VND': 0.00018
        }
    },
    'vietnamese_sessions': [
        {'id': 1, 'session_date': (date.today() - timedelta(days=1)).isoformat(), 'minutes': 45, 'session_type': 'duolingo', 'focus_area': 'Basic phrases'},
        {'id': 2, 'session_date': (date.today() - timedelta(days=2)).isoformat(), 'minutes': 30, 'session_type': 'podcast', 'focus_area': 'Listening'},
        {'id': 3, 'session_date': (date.today() - timedelta(days=3)).isoformat(), 'minutes': 60, 'session_type': 'tutoring', 'focus_area': 'Conversation'},
    ],
    'python_sessions': [
        {'id': 1, 'session_date': (date.today() - timedelta(days=1)).isoformat(), 'hours': 2, 'topic': 'Pandas DataFrames', 'notes': 'Learned about filtering and groupby'},
        {'id': 2, 'session_date': (date.today() - timedelta(days=3)).isoformat(), 'hours': 1.5, 'topic': 'Flask basics', 'notes': 'Created first routes'},
    ],
    'freelance_projects': [
        {'id': 1, 'title': 'Data Analysis Report', 'project_date': (date.today() - timedelta(days=5)).isoformat(), 'amount': 1500, 'hours': 8, 'platform': 'upwork'},
        {'id': 2, 'title': 'Web Scraping Script', 'project_date': (date.today() - timedelta(days=15)).isoformat(), 'amount': 800, 'hours': 4, 'platform': 'fiverr'},
    ],
    'milestones': [
        {'id': 1, 'title': 'Complete Python Basics', 'target_date': '2025-02-28', 'category': 'python', 'notes': 'Finish all beginner modules', 'completed': True},
        {'id': 2, 'title': 'First Freelance Client', 'target_date': '2025-03-15', 'category': 'freelance', 'notes': '', 'completed': True},
        {'id': 3, 'title': 'Vietnamese A1 Level', 'target_date': '2025-06-01', 'category': 'vietnamese', 'notes': 'Basic conversation ability', 'completed': False},
        {'id': 4, 'title': 'Save €5,000', 'target_date': '2025-08-01', 'category': 'financial', 'notes': '', 'completed': False},
    ],
    'notes': [
        {'id': 1, 'title': 'Hanoi Districts Research', 'category': 'relocation', 'content': 'Tay Ho - expat area, expensive. Ba Dinh - central, good cafes. Hoan Kiem - tourist area.', 'created_at': datetime.now().isoformat()},
        {'id': 2, 'title': 'Vietnamese Learning Resources', 'category': 'learning', 'content': 'Duolingo, VietnamesePod101, italki tutors', 'created_at': datetime.now().isoformat()},
    ],
    'learning_path': [
        {'skill_id': 'python_basics', 'skill_name': 'Python Basics & Syntax', 'phase': 1, 'completed': True, 'project_url': None},
        {'skill_id': 'data_structures', 'skill_name': 'Data Structures (Lists, Dicts, Sets)', 'phase': 1, 'completed': True, 'project_url': None},
        {'skill_id': 'functions_oop', 'skill_name': 'Functions & OOP', 'phase': 1, 'completed': True, 'project_url': None},
        {'skill_id': 'file_io', 'skill_name': 'File I/O & CSV Processing', 'phase': 1, 'completed': False, 'project_url': None},
        {'skill_id': 'error_handling', 'skill_name': 'Error Handling & Debugging', 'phase': 1, 'completed': False, 'project_url': None},
        {'skill_id': 'pandas_basics', 'skill_name': 'Pandas Basics', 'phase': 2, 'completed': False, 'project_url': None},
        {'skill_id': 'data_visualization', 'skill_name': 'Data Visualization (Matplotlib/Plotly)', 'phase': 2, 'completed': False, 'project_url': None},
        {'skill_id': 'web_scraping', 'skill_name': 'Web Scraping (BeautifulSoup/Selenium)', 'phase': 2, 'completed': False, 'project_url': None},
        {'skill_id': 'apis_json', 'skill_name': 'APIs & JSON', 'phase': 2, 'completed': False, 'project_url': None},
        {'skill_id': 'excel_automation', 'skill_name': 'Excel Automation (openpyxl)', 'phase': 3, 'completed': False, 'project_url': None},
        {'skill_id': 'pdf_generation', 'skill_name': 'PDF Generation', 'phase': 3, 'completed': False, 'project_url': None},
        {'skill_id': 'database_basics', 'skill_name': 'Database Basics (SQLite/PostgreSQL)', 'phase': 3, 'completed': False, 'project_url': None},
        {'skill_id': 'flask_basics', 'skill_name': 'Flask Web Apps', 'phase': 3, 'completed': False, 'project_url': None},
    ]
}

# ID counters
COUNTERS = {
    'vietnamese': 4,
    'python': 3,
    'freelance': 3,
    'milestones': 5,
    'notes': 3
}

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

def get_week_dates():
    """Get current week start and end dates."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def get_month_start():
    """Get first day of current month."""
    return date.today().replace(day=1)


def calculate_streak():
    """Calculate Vietnamese practice streak."""
    sessions = DATA['vietnamese_sessions']
    if not sessions:
        return 0

    session_dates = set(s['session_date'] for s in sessions)
    today = date.today()
    streak = 0
    current_date = today

    # Check if practiced today or yesterday
    if today.isoformat() not in session_dates:
        current_date = today - timedelta(days=1)
        if current_date.isoformat() not in session_dates:
            return 0

    while current_date.isoformat() in session_dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak


def calculate_streak_with_grace():
    """Calculate streak with 1-day grace period."""
    sessions = DATA['vietnamese_sessions']
    if not sessions:
        return {'streak': 0, 'at_risk': False, 'grace_active': False, 'practiced_today': False}

    session_dates = set(s['session_date'] for s in sessions)
    today = date.today()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)

    practiced_today = today.isoformat() in session_dates
    practiced_yesterday = yesterday.isoformat() in session_dates
    practiced_day_before = day_before.isoformat() in session_dates

    # Calculate base streak
    streak = 0
    if practiced_today:
        current_date = today
        while current_date.isoformat() in session_dates:
            streak += 1
            current_date -= timedelta(days=1)
        return {'streak': streak, 'at_risk': False, 'grace_active': False, 'practiced_today': True}

    # Grace period: didn't practice today but did yesterday
    if practiced_yesterday:
        current_date = yesterday
        while current_date.isoformat() in session_dates:
            streak += 1
            current_date -= timedelta(days=1)
        return {'streak': streak, 'at_risk': True, 'grace_active': True, 'practiced_today': False}

    # Streak broken (missed 2+ days)
    return {'streak': 0, 'at_risk': False, 'grace_active': False, 'practiced_today': False}


def get_recommendations():
    """Get smart recommendations based on current progress."""
    settings = DATA['settings']
    today = date.today()
    today_str = today.isoformat()
    target_date = datetime.strptime(settings['target_date'], '%Y-%m-%d').date()
    week_start, week_end = get_week_dates()
    month_start = get_month_start()

    # Calculate weekly progress
    py_week = sum(s['hours'] for s in DATA['python_sessions']
                  if week_start.isoformat() <= s['session_date'] <= week_end.isoformat())
    vn_week_mins = sum(s['minutes'] for s in DATA['vietnamese_sessions']
                       if week_start.isoformat() <= s['session_date'] <= week_end.isoformat())
    vn_week = vn_week_mins / 60  # Convert to hours

    py_target = settings['python_weekly_target']
    vn_target = settings['vietnamese_weekly_target']

    py_percent = min(100, int((py_week / py_target) * 100)) if py_target > 0 else 100
    vn_percent = min(100, int((vn_week / vn_target) * 100)) if vn_target > 0 else 100

    # Income progress
    income_month = sum(p['amount'] for p in DATA['freelance_projects']
                       if p['project_date'] >= month_start.isoformat())
    income_target = settings['income_target']
    income_percent = min(100, int((income_month / income_target) * 100)) if income_target > 0 else 100

    # Streak with grace period
    streak_info = calculate_streak_with_grace()

    # Calculate pace for Vietnamese (600 hours to B1)
    vn_total_hours = sum(s['minutes'] for s in DATA['vietnamese_sessions']) / 60
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
        mins_today = sum(s['minutes'] for s in DATA['vietnamese_sessions']
                         if s['session_date'] == date.today().isoformat())
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
        gap = 100 - vn_percent
        return {
            'area': 'vietnamese',
            'priority': 'high',
            'reason': f"You're at {vn_percent}% of your Vietnamese target (vs {py_percent}% Python)",
            'suggestion': random.choice(suggestions['vietnamese']),
            'icon': '🇻🇳'
        }

    if py_percent < vn_percent and py_percent < 70:
        gap = 100 - py_percent
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
            return update_settings()
        return get_settings()
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
        'vietnameseSessions': DATA['vietnamese_sessions'],
        'pythonSessions': DATA['python_sessions'],
        'freelanceProjects': DATA['freelance_projects'],
        'milestones': DATA['milestones'],
        'notes': DATA['notes']
    })


def get_stats():
    """Get dashboard statistics."""
    settings = DATA['settings']
    today = date.today()
    target_date = datetime.strptime(settings['target_date'], '%Y-%m-%d').date()
    week_start, week_end = get_week_dates()
    month_start = get_month_start()

    # Vietnamese stats
    vn_total = sum(s['minutes'] for s in DATA['vietnamese_sessions'])
    vn_week = sum(s['minutes'] for s in DATA['vietnamese_sessions']
                  if week_start.isoformat() <= s['session_date'] <= week_end.isoformat())

    # Python stats
    py_total = sum(s['hours'] for s in DATA['python_sessions'])
    py_week = sum(s['hours'] for s in DATA['python_sessions']
                  if week_start.isoformat() <= s['session_date'] <= week_end.isoformat())

    # Freelance stats
    fl_total = sum(p['amount'] for p in DATA['freelance_projects'])
    fl_month = sum(p['amount'] for p in DATA['freelance_projects']
                   if p['project_date'] >= month_start.isoformat())
    fl_hours = sum(p['hours'] or 0 for p in DATA['freelance_projects'])
    avg_rate = fl_total / fl_hours if fl_hours > 0 else 0

    # Learning path
    completed_skills = sum(1 for s in DATA['learning_path'] if s['completed'])
    total_skills = len(DATA['learning_path'])
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
            'incomeTotal': fl_total,
            'incomeThisMonth': fl_month,
            'incomeTarget': settings['income_target'],
            'totalProjects': len(DATA['freelance_projects']),
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
    settings = DATA['settings']
    today = date.today()
    today_str = today.isoformat()
    target_date = datetime.strptime(settings['target_date'], '%Y-%m-%d').date()
    week_start, week_end = get_week_dates()
    month_start = get_month_start()

    # Python today/week
    py_today = [s for s in DATA['python_sessions'] if s['session_date'] == today_str]
    py_today_hours = sum(s['hours'] for s in py_today)
    py_week = sum(s['hours'] for s in DATA['python_sessions']
                  if week_start.isoformat() <= s['session_date'] <= week_end.isoformat())

    # Vietnamese today/week
    vn_today = [s for s in DATA['vietnamese_sessions'] if s['session_date'] == today_str]
    vn_today_mins = sum(s['minutes'] for s in vn_today)
    vn_week = sum(s['minutes'] for s in DATA['vietnamese_sessions']
                  if week_start.isoformat() <= s['session_date'] <= week_end.isoformat())

    # Income
    income_month = sum(p['amount'] for p in DATA['freelance_projects']
                       if p['project_date'] >= month_start.isoformat())
    income_gap = max(0, settings['income_target'] - income_month)
    income_progress = min(100, int((income_month / settings['income_target']) * 100)) if settings['income_target'] > 0 else 0

    # Upcoming milestones
    upcoming = [m for m in DATA['milestones']
                if not m['completed'] and m['target_date'] <= week_end.isoformat()]

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


def get_settings():
    """Get settings."""
    return jsonify(DATA['settings'])


def update_settings():
    """Update settings."""
    data = request.get_json()
    for key, value in data.items():
        if key in DATA['settings']:
            DATA['settings'][key] = value
    return jsonify({'success': True})


def handle_milestones():
    """Handle milestone CRUD."""
    if request.method == 'POST':
        data = request.get_json()
        milestone = {
            'id': COUNTERS['milestones'],
            'title': data['title'],
            'target_date': data['target_date'],
            'category': data.get('category'),
            'notes': data.get('notes', ''),
            'completed': False
        }
        COUNTERS['milestones'] += 1
        DATA['milestones'].append(milestone)
        return jsonify({'success': True, 'id': milestone['id']})

    elif request.method == 'PUT':
        milestone_id = int(request.args.get('id'))
        data = request.get_json()
        for m in DATA['milestones']:
            if m['id'] == milestone_id:
                m.update({k: v for k, v in data.items() if k != 'id'})
                break
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        milestone_id = int(request.args.get('id'))
        DATA['milestones'] = [m for m in DATA['milestones'] if m['id'] != milestone_id]
        return jsonify({'success': True})

    return jsonify(DATA['milestones'])


def handle_python():
    """Handle Python session CRUD."""
    if request.method == 'POST':
        data = request.get_json()
        session = {
            'id': COUNTERS['python'],
            'session_date': data['session_date'],
            'hours': data['hours'],
            'topic': data.get('topic', ''),
            'notes': data.get('notes', '')
        }
        COUNTERS['python'] += 1
        DATA['python_sessions'].insert(0, session)
        return jsonify({'success': True, 'id': session['id']})

    elif request.method == 'DELETE':
        session_id = int(request.args.get('id'))
        DATA['python_sessions'] = [s for s in DATA['python_sessions'] if s['id'] != session_id]
        return jsonify({'success': True})

    return jsonify(DATA['python_sessions'])


def handle_vietnamese():
    """Handle Vietnamese session CRUD."""
    if request.method == 'POST':
        data = request.get_json()
        session = {
            'id': COUNTERS['vietnamese'],
            'session_date': data['session_date'],
            'minutes': data['minutes'],
            'session_type': data.get('session_type', ''),
            'focus_area': data.get('focus_area', '')
        }
        COUNTERS['vietnamese'] += 1
        DATA['vietnamese_sessions'].insert(0, session)
        return jsonify({'success': True, 'id': session['id']})

    elif request.method == 'DELETE':
        session_id = int(request.args.get('id'))
        DATA['vietnamese_sessions'] = [s for s in DATA['vietnamese_sessions'] if s['id'] != session_id]
        return jsonify({'success': True})

    return jsonify(DATA['vietnamese_sessions'])


def handle_freelance():
    """Handle freelance project CRUD."""
    if request.method == 'POST':
        data = request.get_json()
        project = {
            'id': COUNTERS['freelance'],
            'title': data['title'],
            'project_date': data['project_date'],
            'amount': data['amount'],
            'hours': data.get('hours'),
            'platform': data.get('platform', ''),
            'description': data.get('description', '')
        }
        COUNTERS['freelance'] += 1
        DATA['freelance_projects'].insert(0, project)
        return jsonify({'success': True, 'id': project['id']})

    elif request.method == 'DELETE':
        project_id = int(request.args.get('id'))
        DATA['freelance_projects'] = [p for p in DATA['freelance_projects'] if p['id'] != project_id]
        return jsonify({'success': True})

    return jsonify(DATA['freelance_projects'])


def handle_notes():
    """Handle notes CRUD."""
    if request.method == 'POST':
        data = request.get_json()
        note = {
            'id': COUNTERS['notes'],
            'title': data['title'],
            'category': data.get('category', ''),
            'content': data.get('content', ''),
            'created_at': datetime.now().isoformat()
        }
        COUNTERS['notes'] += 1
        DATA['notes'].insert(0, note)
        return jsonify({'success': True, 'id': note['id']})

    elif request.method == 'PUT':
        note_id = int(request.args.get('id'))
        data = request.get_json()
        for n in DATA['notes']:
            if n['id'] == note_id:
                n.update({k: v for k, v in data.items() if k != 'id'})
                break
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        note_id = int(request.args.get('id'))
        DATA['notes'] = [n for n in DATA['notes'] if n['id'] != note_id]
        return jsonify({'success': True})

    return jsonify(DATA['notes'])


def handle_learning_path():
    """Handle learning path."""
    if request.method == 'PUT':
        data = request.get_json()
        skill_id = data.get('skill_id')
        for skill in DATA['learning_path']:
            if skill['skill_id'] == skill_id:
                skill['completed'] = data.get('completed', False)
                if data.get('project_url'):
                    skill['project_url'] = data['project_url']
                break
        return jsonify({'success': True})

    return jsonify(DATA['learning_path'])


# ============ CURRENCY ENDPOINT ============

@api_bp.route('/currency.php', methods=['GET', 'PUT'])
def currency():
    """Currency API endpoint."""
    action = request.args.get('action')

    # Get exchange rates from settings (user-configurable)
    rates = DATA['settings'].get('exchange_rates', {
        'EUR': 4.97,
        'USD': 4.55,
        'VND': 0.00018
    })

    if action == 'rates':
        if request.method == 'PUT':
            # Update exchange rates
            data = request.get_json()
            if data and 'rates' in data:
                for currency_code, rate in data['rates'].items():
                    if currency_code in ['EUR', 'USD', 'VND']:
                        DATA['settings']['exchange_rates'][currency_code] = float(rate)
                return jsonify({
                    'success': True,
                    'rates': DATA['settings']['exchange_rates'],
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
