from flask import Blueprint, render_template, send_from_directory
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/index.html')
def index():
    return render_template('hanoi-relocation/index.html')


@main_bp.route('/settings')
def settings():
    return render_template('hanoi-relocation/settings.html')


@main_bp.route('/learning-path')
def learning_path():
    return render_template('hanoi-relocation/learning-path.html')


@main_bp.route('/login')
def login_page():
    return render_template('login.html')
