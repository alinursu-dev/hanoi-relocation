"""
SQLite Database module for Hanoi Relocation Dashboard.
Replaces in-memory DATA dict with persistent storage.
"""
import sqlite3
import os
import json
from datetime import datetime, date, timedelta
from contextlib import contextmanager

# Database file location (project root)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'hanoi.db')


@contextmanager
def get_db():
    """Get a database connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def dict_from_row(row):
    """Convert a sqlite3.Row to a plain dict."""
    if row is None:
        return None
    return dict(row)


def rows_to_list(rows):
    """Convert a list of sqlite3.Row to a list of dicts."""
    return [dict(r) for r in rows]


def init_db():
    """Create all tables and seed with default data if empty."""
    with get_db() as conn:
        # ---- Settings (key-value store) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # ---- Vietnamese Sessions ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vietnamese_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TEXT NOT NULL,
                minutes INTEGER NOT NULL,
                session_type TEXT DEFAULT '',
                focus_area TEXT DEFAULT ''
            )
        """)

        # ---- Python Sessions ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS python_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TEXT NOT NULL,
                hours REAL NOT NULL,
                topic TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            )
        """)

        # ---- Freelance Projects ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS freelance_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                project_date TEXT NOT NULL,
                amount REAL NOT NULL,
                hours REAL DEFAULT 0,
                platform TEXT DEFAULT '',
                description TEXT DEFAULT ''
            )
        """)

        # ---- Milestones ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                target_date TEXT NOT NULL,
                category TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                completed INTEGER DEFAULT 0
            )
        """)

        # ---- Notes ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT DEFAULT '',
                content TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)

        # ---- Learning Path ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_path (
                skill_id TEXT PRIMARY KEY,
                skill_name TEXT NOT NULL,
                phase INTEGER NOT NULL,
                completed INTEGER DEFAULT 0,
                project_url TEXT
            )
        """)

        # ---- Seed data if tables are empty ----
        _seed_if_empty(conn)


def _seed_if_empty(conn):
    """Insert default data into empty tables."""
    today = date.today()

    # Settings
    count = conn.execute("SELECT COUNT(*) FROM settings").fetchone()[0]
    if count == 0:
        defaults = {
            'target_date': '2026-10-31',
            'income_target': '7500',
            'python_weekly_target': '8',
            'vietnamese_weekly_target': '7',
            'savings': '27500',
            'monthly_burn': '3000',
            'preferred_currency': 'EUR',
            'github_username': '',
            'exchange_rate_EUR': '4.97',
            'exchange_rate_USD': '4.55',
            'exchange_rate_VND': '0.00018',
        }
        conn.executemany(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            defaults.items()
        )

    # Vietnamese sessions
    count = conn.execute("SELECT COUNT(*) FROM vietnamese_sessions").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO vietnamese_sessions (session_date, minutes, session_type, focus_area) VALUES (?, ?, ?, ?)",
            [
                ((today - timedelta(days=1)).isoformat(), 45, 'duolingo', 'Basic phrases'),
                ((today - timedelta(days=2)).isoformat(), 30, 'podcast', 'Listening'),
                ((today - timedelta(days=3)).isoformat(), 60, 'tutoring', 'Conversation'),
            ]
        )

    # Python sessions
    count = conn.execute("SELECT COUNT(*) FROM python_sessions").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO python_sessions (session_date, hours, topic, notes) VALUES (?, ?, ?, ?)",
            [
                ((today - timedelta(days=1)).isoformat(), 2, 'Pandas DataFrames', 'Learned about filtering and groupby'),
                ((today - timedelta(days=3)).isoformat(), 1.5, 'Flask basics', 'Created first routes'),
            ]
        )

    # Freelance projects
    count = conn.execute("SELECT COUNT(*) FROM freelance_projects").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO freelance_projects (title, project_date, amount, hours, platform) VALUES (?, ?, ?, ?, ?)",
            [
                ('Data Analysis Report', (today - timedelta(days=5)).isoformat(), 1500, 8, 'upwork'),
                ('Web Scraping Script', (today - timedelta(days=15)).isoformat(), 800, 4, 'fiverr'),
            ]
        )

    # Milestones
    count = conn.execute("SELECT COUNT(*) FROM milestones").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO milestones (title, target_date, category, notes, completed) VALUES (?, ?, ?, ?, ?)",
            [
                ('Complete Python Basics', '2025-02-28', 'python', 'Finish all beginner modules', 1),
                ('First Freelance Client', '2025-03-15', 'freelance', '', 1),
                ('Vietnamese A1 Level', '2025-06-01', 'vietnamese', 'Basic conversation ability', 0),
                ('Save €5,000', '2025-08-01', 'financial', '', 0),
            ]
        )

    # Notes
    count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    if count == 0:
        now = datetime.now().isoformat()
        conn.executemany(
            "INSERT INTO notes (title, category, content, created_at) VALUES (?, ?, ?, ?)",
            [
                ('Hanoi Districts Research', 'relocation',
                 'Tay Ho - expat area, expensive. Ba Dinh - central, good cafes. Hoan Kiem - tourist area.', now),
                ('Vietnamese Learning Resources', 'learning',
                 'Duolingo, VietnamesePod101, italki tutors', now),
            ]
        )

    # Learning path
    count = conn.execute("SELECT COUNT(*) FROM learning_path").fetchone()[0]
    if count == 0:
        skills = [
            ('python_basics', 'Python Basics & Syntax', 1, 1, None),
            ('data_structures', 'Data Structures (Lists, Dicts, Sets)', 1, 1, None),
            ('functions_oop', 'Functions & OOP', 1, 1, None),
            ('file_io', 'File I/O & CSV Processing', 1, 0, None),
            ('error_handling', 'Error Handling & Debugging', 1, 0, None),
            ('pandas_basics', 'Pandas Basics', 2, 0, None),
            ('data_visualization', 'Data Visualization (Matplotlib/Plotly)', 2, 0, None),
            ('web_scraping', 'Web Scraping (BeautifulSoup/Selenium)', 2, 0, None),
            ('apis_json', 'APIs & JSON', 2, 0, None),
            ('excel_automation', 'Excel Automation (openpyxl)', 3, 0, None),
            ('pdf_generation', 'PDF Generation', 3, 0, None),
            ('database_basics', 'Database Basics (SQLite/PostgreSQL)', 3, 0, None),
            ('flask_basics', 'Flask Web Apps', 3, 0, None),
        ]
        conn.executemany(
            "INSERT INTO learning_path (skill_id, skill_name, phase, completed, project_url) VALUES (?, ?, ?, ?, ?)",
            skills
        )


# ============ SETTINGS HELPERS ============

def get_setting(key, default=None):
    """Get a single setting value."""
    with get_db() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row['value'] if row else default


def get_setting_float(key, default=0.0):
    """Get a setting as float."""
    val = get_setting(key)
    return float(val) if val is not None else default


def get_setting_int(key, default=0):
    """Get a setting as int."""
    val = get_setting(key)
    return int(float(val)) if val is not None else default


def get_all_settings():
    """Get all settings as a dict, structured like the old DATA['settings']."""
    with get_db() as conn:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        raw = {r['key']: r['value'] for r in rows}

    return {
        'target_date': raw.get('target_date', '2026-10-31'),
        'income_target': float(raw.get('income_target', 7500)),
        'python_weekly_target': float(raw.get('python_weekly_target', 8)),
        'vietnamese_weekly_target': float(raw.get('vietnamese_weekly_target', 7)),
        'savings': float(raw.get('savings', 27500)),
        'monthly_burn': float(raw.get('monthly_burn', 3000)),
        'preferred_currency': raw.get('preferred_currency', 'EUR'),
        'github_username': raw.get('github_username', ''),
        'exchange_rates': {
            'EUR': float(raw.get('exchange_rate_EUR', 4.97)),
            'USD': float(raw.get('exchange_rate_USD', 4.55)),
            'VND': float(raw.get('exchange_rate_VND', 0.00018)),
        }
    }


def update_settings(data: dict):
    """Update settings from a dict."""
    # Map nested exchange_rates to flat keys
    exchange_rates = data.pop('exchange_rates', None)
    with get_db() as conn:
        for key, value in data.items():
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, str(value))
            )
        if exchange_rates:
            for curr, rate in exchange_rates.items():
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (f'exchange_rate_{curr}', str(rate))
                )


# ============ VIETNAMESE SESSIONS ============

def get_vietnamese_sessions():
    """Get all Vietnamese sessions."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM vietnamese_sessions ORDER BY session_date DESC").fetchall()
        return rows_to_list(rows)


def get_vietnamese_sessions_by_date(session_date: str):
    """Get Vietnamese sessions for a specific date."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM vietnamese_sessions WHERE session_date = ?",
            (session_date,)
        ).fetchall()
        return rows_to_list(rows)


def get_vietnamese_sessions_between(start_date: str, end_date: str):
    """Get Vietnamese sessions between two dates."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM vietnamese_sessions WHERE session_date BETWEEN ? AND ?",
            (start_date, end_date)
        ).fetchall()
        return rows_to_list(rows)


def get_vietnamese_session_dates():
    """Get distinct dates that have Vietnamese sessions."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT session_date FROM vietnamese_sessions"
        ).fetchall()
        return set(r['session_date'] for r in rows)


def sum_vietnamese_minutes(start_date: str = None, end_date: str = None):
    """Sum Vietnamese minutes, optionally between dates."""
    with get_db() as conn:
        if start_date and end_date:
            row = conn.execute(
                "SELECT COALESCE(SUM(minutes), 0) as total FROM vietnamese_sessions WHERE session_date BETWEEN ? AND ?",
                (start_date, end_date)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COALESCE(SUM(minutes), 0) as total FROM vietnamese_sessions"
            ).fetchone()
        return row['total']


def create_vietnamese_session(session_date, minutes, session_type='', focus_area=''):
    """Create a new Vietnamese session."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO vietnamese_sessions (session_date, minutes, session_type, focus_area) VALUES (?, ?, ?, ?)",
            (session_date, minutes, session_type, focus_area)
        )
        return cursor.lastrowid


def delete_vietnamese_session(session_id):
    """Delete a Vietnamese session by ID."""
    with get_db() as conn:
        conn.execute("DELETE FROM vietnamese_sessions WHERE id = ?", (session_id,))


# ============ PYTHON SESSIONS ============

def get_python_sessions():
    """Get all Python sessions."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM python_sessions ORDER BY session_date DESC").fetchall()
        return rows_to_list(rows)


def get_python_sessions_by_date(session_date: str):
    """Get Python sessions for a specific date."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM python_sessions WHERE session_date = ?",
            (session_date,)
        ).fetchall()
        return rows_to_list(rows)


def get_python_sessions_between(start_date: str, end_date: str):
    """Get Python sessions between two dates."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM python_sessions WHERE session_date BETWEEN ? AND ?",
            (start_date, end_date)
        ).fetchall()
        return rows_to_list(rows)


def sum_python_hours(start_date: str = None, end_date: str = None):
    """Sum Python hours, optionally between dates."""
    with get_db() as conn:
        if start_date and end_date:
            row = conn.execute(
                "SELECT COALESCE(SUM(hours), 0) as total FROM python_sessions WHERE session_date BETWEEN ? AND ?",
                (start_date, end_date)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COALESCE(SUM(hours), 0) as total FROM python_sessions"
            ).fetchone()
        return row['total']


def create_python_session(session_date, hours, topic='', notes=''):
    """Create a new Python session."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO python_sessions (session_date, hours, topic, notes) VALUES (?, ?, ?, ?)",
            (session_date, hours, topic, notes)
        )
        return cursor.lastrowid


def delete_python_session(session_id):
    """Delete a Python session by ID."""
    with get_db() as conn:
        conn.execute("DELETE FROM python_sessions WHERE id = ?", (session_id,))


# ============ FREELANCE PROJECTS ============

def get_freelance_projects():
    """Get all freelance projects."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM freelance_projects ORDER BY project_date DESC").fetchall()
        return rows_to_list(rows)


def get_freelance_income_since(start_date: str):
    """Get total income from freelance projects since a date."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM freelance_projects WHERE project_date >= ?",
            (start_date,)
        ).fetchone()
        return row['total']


def get_freelance_stats():
    """Get aggregate freelance stats."""
    with get_db() as conn:
        row = conn.execute("""
            SELECT
                COALESCE(SUM(amount), 0) as total_income,
                COALESCE(SUM(hours), 0) as total_hours,
                COUNT(*) as total_projects
            FROM freelance_projects
        """).fetchone()
        return dict(row)


def create_freelance_project(title, project_date, amount, hours=0, platform='', description=''):
    """Create a new freelance project."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO freelance_projects (title, project_date, amount, hours, platform, description) VALUES (?, ?, ?, ?, ?, ?)",
            (title, project_date, amount, hours, platform, description)
        )
        return cursor.lastrowid


def delete_freelance_project(project_id):
    """Delete a freelance project by ID."""
    with get_db() as conn:
        conn.execute("DELETE FROM freelance_projects WHERE id = ?", (project_id,))


# ============ MILESTONES ============

def get_milestones():
    """Get all milestones."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM milestones ORDER BY target_date").fetchall()
        result = rows_to_list(rows)
        for m in result:
            m['completed'] = bool(m['completed'])
        return result


def get_milestones_upcoming(end_date: str):
    """Get incomplete milestones up to end_date."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM milestones WHERE completed = 0 AND target_date <= ? ORDER BY target_date",
            (end_date,)
        ).fetchall()
        result = rows_to_list(rows)
        for m in result:
            m['completed'] = bool(m['completed'])
        return result


def create_milestone(title, target_date, category='', notes=''):
    """Create a new milestone."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO milestones (title, target_date, category, notes, completed) VALUES (?, ?, ?, ?, 0)",
            (title, target_date, category, notes)
        )
        return cursor.lastrowid


def update_milestone(milestone_id, data: dict):
    """Update a milestone."""
    with get_db() as conn:
        for key, value in data.items():
            if key == 'id':
                continue
            if key == 'completed':
                value = 1 if value else 0
            conn.execute(
                f"UPDATE milestones SET {key} = ? WHERE id = ?",
                (value, milestone_id)
            )


def delete_milestone(milestone_id):
    """Delete a milestone by ID."""
    with get_db() as conn:
        conn.execute("DELETE FROM milestones WHERE id = ?", (milestone_id,))


# ============ NOTES ============

def get_notes():
    """Get all notes."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM notes ORDER BY created_at DESC").fetchall()
        return rows_to_list(rows)


def create_note(title, category='', content=''):
    """Create a new note."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, category, content, created_at) VALUES (?, ?, ?, ?)",
            (title, category, content, datetime.now().isoformat())
        )
        return cursor.lastrowid


def update_note(note_id, data: dict):
    """Update a note."""
    with get_db() as conn:
        for key, value in data.items():
            if key in ('id', 'created_at'):
                continue
            conn.execute(
                f"UPDATE notes SET {key} = ? WHERE id = ?",
                (value, note_id)
            )


def delete_note(note_id):
    """Delete a note by ID."""
    with get_db() as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))


# ============ LEARNING PATH ============

def get_learning_path():
    """Get all learning path skills."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM learning_path ORDER BY phase, skill_id").fetchall()
        result = rows_to_list(rows)
        for s in result:
            s['completed'] = bool(s['completed'])
        return result


def update_learning_skill(skill_id, completed=None, project_url=None):
    """Update a learning path skill."""
    with get_db() as conn:
        if completed is not None:
            conn.execute(
                "UPDATE learning_path SET completed = ? WHERE skill_id = ?",
                (1 if completed else 0, skill_id)
            )
        if project_url is not None:
            conn.execute(
                "UPDATE learning_path SET project_url = ? WHERE skill_id = ?",
                (project_url, skill_id)
            )


# ============ STREAK CALCULATIONS ============

def calculate_streak():
    """Calculate Vietnamese practice streak from database."""
    session_dates = get_vietnamese_session_dates()
    if not session_dates:
        return 0

    today = date.today()
    streak = 0
    current_date = today

    if today.isoformat() not in session_dates:
        current_date = today - timedelta(days=1)
        if current_date.isoformat() not in session_dates:
            return 0

    while current_date.isoformat() in session_dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak


def calculate_streak_with_grace():
    """Calculate streak with 1-day grace period from database."""
    session_dates = get_vietnamese_session_dates()
    if not session_dates:
        return {'streak': 0, 'at_risk': False, 'grace_active': False, 'practiced_today': False}

    today = date.today()
    yesterday = today - timedelta(days=1)

    practiced_today = today.isoformat() in session_dates
    practiced_yesterday = yesterday.isoformat() in session_dates

    streak = 0
    if practiced_today:
        current_date = today
        while current_date.isoformat() in session_dates:
            streak += 1
            current_date -= timedelta(days=1)
        return {'streak': streak, 'at_risk': False, 'grace_active': False, 'practiced_today': True}

    if practiced_yesterday:
        current_date = yesterday
        while current_date.isoformat() in session_dates:
            streak += 1
            current_date -= timedelta(days=1)
        return {'streak': streak, 'at_risk': True, 'grace_active': True, 'practiced_today': False}

    return {'streak': 0, 'at_risk': False, 'grace_active': False, 'practiced_today': False}


# ============ WEEK / MONTH HELPERS ============

def get_week_dates():
    """Get current week start and end dates."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def get_month_start():
    """Get first day of current month."""
    return date.today().replace(day=1)
