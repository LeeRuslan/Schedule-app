from flask import Blueprint, render_template
from models import HistoryLog

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    return render_template('index.html')


@pages_bp.route('/teachers')
def teachers_page():
    return render_template('teachers.html')


@pages_bp.route('/subjects')
def subjects_page():
    return render_template('subjects.html')


@pages_bp.route('/groups')
def groups_page():
    return render_template('groups.html')


@pages_bp.route('/classrooms')
def classrooms_page():
    return render_template('classrooms.html')


@pages_bp.route('/settings')
def settings_page():
    return render_template('settings.html')