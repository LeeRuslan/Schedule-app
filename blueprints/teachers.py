from flask import Blueprint, request, jsonify
from extensions import db
from models import Teacher, Subject
from utils import log_history

teachers_bp = Blueprint('teachers', __name__, url_prefix='/api/teachers')


@teachers_bp.route('', methods=['GET'])
def get_teachers():
    teachers = Teacher.query.order_by(Teacher.name).all()
    return jsonify([{
        'id': t.id, 'name': t.name, 'short_name': t.short_name, 'color': t.color,
        'subjects': [{'id': s.id, 'name': s.name, 'short_name': s.short_name} for s in t.subjects]
    } for t in teachers])


@teachers_bp.route('/<int:id>/subjects', methods=['GET'])
def get_teacher_subjects(id):
    teacher = Teacher.query.get_or_404(id)
    return jsonify([{
        'id': s.id, 'name': s.name, 'short_name': s.short_name
    } for s in teacher.subjects])


@teachers_bp.route('', methods=['POST'])
def create_teacher():
    data = request.json
    teacher = Teacher(
        name=data['name'],
        short_name=data.get('short_name'),
        color=data.get('color', '#3b82f6')
    )
    if 'subject_ids' in data:
        teacher.subjects = Subject.query.filter(Subject.id.in_(data['subject_ids'])).all()
    db.session.add(teacher)
    db.session.commit()
    log_history('create', 'teacher', teacher.id, data)
    return jsonify({'id': teacher.id}), 201


@teachers_bp.route('/<int:id>', methods=['PUT'])
def update_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    data = request.json
    teacher.name = data.get('name', teacher.name)
    teacher.short_name = data.get('short_name', teacher.short_name)
    teacher.color = data.get('color', teacher.color)
    if 'subject_ids' in data:
        teacher.subjects = Subject.query.filter(Subject.id.in_(data['subject_ids'])).all()
    db.session.commit()
    log_history('update', 'teacher', id, data)
    return jsonify({'status': 'ok'})


@teachers_bp.route('/<int:id>', methods=['DELETE'])
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    log_history('delete', 'teacher', id, {})
    return jsonify({'status': 'ok'})