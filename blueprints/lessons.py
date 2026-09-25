from flask import Blueprint, request, jsonify
from extensions import db
from models import Lesson
from utils import log_history, check_conflicts

lessons_bp = Blueprint('lessons', __name__, url_prefix='/api/lessons')


@lessons_bp.route('', methods=['GET'])
def get_lessons():
    lessons = Lesson.query.all()
    return jsonify([{
        'id': l.id,
        'group_id': l.group_id,
        'teacher_id': l.teacher_id,
        'subject_id': l.subject_id,
        'classroom_id': l.classroom_id,
        'day': l.day,
        'week1_lesson': l.week1_lesson,
        'week2_lesson': l.week2_lesson,
        'lesson_type': l.lesson_type,
        'teacher_name': l.teacher.name if l.teacher else '',
        'teacher_short': l.teacher.short_name if l.teacher else '',
        'teacher_color': l.teacher.color if l.teacher else '#ccc',
        'subject_name': l.subject.name if l.subject else '',
        'subject_short': l.subject.short_name if l.subject else '',
        'classroom_name': l.classroom.name if l.classroom else '',
        'group_name': l.group.name if l.group else ''
    } for l in lessons])


@lessons_bp.route('', methods=['POST'])
def create_lesson():
    data = request.json
    conflict = check_conflicts(data)
    if conflict:
        return jsonify({'error': conflict}), 409
    lesson = Lesson(
        group_id=data['group_id'],
        teacher_id=data['teacher_id'],
        subject_id=data['subject_id'],
        classroom_id=data.get('classroom_id'),
        day=data['day'],
        week1_lesson=data.get('week1_lesson', 0),
        week2_lesson=data.get('week2_lesson', 0),
        lesson_type=data.get('lesson_type', 'Лекция')
    )
    db.session.add(lesson)
    db.session.commit()
    log_history('create', 'lesson', lesson.id, data)
    return jsonify({'id': lesson.id}), 201


@lessons_bp.route('/<int:id>', methods=['GET'])
def get_lesson(id):
    l = Lesson.query.get_or_404(id)
    return jsonify({
        'id': l.id, 'group_id': l.group_id, 'teacher_id': l.teacher_id,
        'subject_id': l.subject_id, 'classroom_id': l.classroom_id,
        'day': l.day, 'week1_lesson': l.week1_lesson,
        'week2_lesson': l.week2_lesson, 'lesson_type': l.lesson_type
    })


@lessons_bp.route('/<int:id>', methods=['PUT'])
def update_lesson(id):
    lesson = Lesson.query.get_or_404(id)
    data = request.json
    merged = {
        'group_id': data.get('group_id', lesson.group_id),
        'teacher_id': data.get('teacher_id', lesson.teacher_id),
        'subject_id': data.get('subject_id', lesson.subject_id),
        'classroom_id': data.get('classroom_id', lesson.classroom_id),
        'day': data.get('day', lesson.day),
        'week1_lesson': data.get('week1_lesson', lesson.week1_lesson),
        'week2_lesson': data.get('week2_lesson', lesson.week2_lesson),
    }
    conflict = check_conflicts(merged, exclude_id=id)
    if conflict:
        return jsonify({'error': conflict}), 409

    for key, value in data.items():
        setattr(lesson, key, value)
    db.session.commit()
    log_history('update', 'lesson', id, data)
    return jsonify({'status': 'ok'})


@lessons_bp.route('/<int:id>', methods=['DELETE'])
def delete_lesson(id):
    lesson = Lesson.query.get_or_404(id)
    db.session.delete(lesson)
    db.session.commit()
    log_history('delete', 'lesson', id, {})
    return jsonify({'status': 'ok'})


@lessons_bp.route('/clear', methods=['POST'])
def clear_lessons():
    count = Lesson.query.delete()
    db.session.commit()
    log_history('delete', 'lessons', 0, {'count': count})
    return jsonify({'status': 'ok', 'deleted': count})