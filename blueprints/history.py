from flask import Blueprint, render_template, jsonify
from models import HistoryLog

history_bp = Blueprint('history', __name__)


# Страница
@history_bp.route('/history')
def history_page():
    logs = HistoryLog.query.order_by(HistoryLog.timestamp.desc()).limit(200).all()
    return render_template('history.html', logs=logs)


# API — на будущее (фильтр, экспорт)
@history_bp.route('/api/history')
def get_history():
    logs = HistoryLog.query.order_by(HistoryLog.timestamp.desc()).limit(200).all()
    return jsonify([{
        'id': l.id,
        'timestamp': l.timestamp.isoformat(),
        'user': l.user,
        'action': l.action,
        'entity_type': l.entity_type,
        'entity_id': l.entity_id,
        'details': l.details
    } for l in logs])