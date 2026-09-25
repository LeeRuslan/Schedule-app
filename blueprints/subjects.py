from flask import Blueprint, request, jsonify
from extensions import db
from models import Subject
from utils import log_history

subjects_bp = Blueprint('subjects', __name__, url_prefix='/api/subjects')


@subjects_bp.route('', methods=['GET'])
def get_subjects():
    subjects = Subject.query.order_by(Subject.name).all()
    return jsonify([{
        'id': s.id, 'name': s.name,
        'short_name': s.short_name, 'lesson_type': s.lesson_type
    } for s in subjects])


@subjects_bp.route('', methods=['POST'])
def create_subject():
    data = request.json
    subject = Subject(
        name=data['name'],
        short_name=data.get('short_name'),
        lesson_type=data.get('lesson_type', 'Лекция')
    )
    db.session.add(subject)
    db.session.commit()
    log_history('create', 'subject', subject.id, data)
    return jsonify({'id': subject.id}), 201


@subjects_bp.route('/<int:id>', methods=['PUT'])
def update_subject(id):
    subject = Subject.query.get_or_404(id)
    data = request.json
    subject.name = data.get('name', subject.name)
    subject.short_name = data.get('short_name', subject.short_name)
    subject.lesson_type = data.get('lesson_type', subject.lesson_type)
    db.session.commit()
    log_history('update', 'subject', id, data)
    return jsonify({'status': 'ok'})


@subjects_bp.route('/<int:id>', methods=['DELETE'])
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    log_history('delete', 'subject', id, {})
    return jsonify({'status': 'ok'})