import os
import json
from flask import Flask, render_template, request, jsonify
from models import db, Group, Teacher, Subject, Classroom, Lesson, HistoryLog
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, 'static'),
    template_folder=os.path.join(BASE_DIR, 'templates')
)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'schedule.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()


# ============ ВСПОМОГАТЕЛЬНОЕ ============
def log_history(action, entity_type, entity_id, details):
    log = HistoryLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=json.dumps(details, ensure_ascii=False)
    )
    db.session.add(log)
    db.session.commit()


# ============ СТРАНИЦЫ ============
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/teachers')
def teachers_page():
    return render_template('teachers.html')


@app.route('/subjects')
def subjects_page():
    return render_template('subjects.html')


@app.route('/groups')
def groups_page():
    return render_template('groups.html')


@app.route('/classrooms')
def classrooms_page():
    return render_template('classrooms.html')


@app.route('/settings')
def settings_page():
    return render_template('settings.html')


@app.route('/history')
def history_page():
    logs = HistoryLog.query.order_by(HistoryLog.timestamp.desc()).limit(200).all()
    return render_template('history.html', logs=logs)


# ============ ГРУППЫ ============
@app.route('/api/groups', methods=['GET'])
def get_groups():
    groups = Group.query.order_by(Group.name).all()
    return jsonify([{'id': g.id, 'name': g.name, 'speciality': g.speciality, 'course': g.course} for g in groups])


@app.route('/api/groups', methods=['POST'])
def create_group():
    data = request.json
    group = Group(name=data['name'], speciality=data.get('speciality'), course=data.get('course'))
    db.session.add(group)
    db.session.commit()
    log_history('create', 'group', group.id, data)
    return jsonify({'id': group.id}), 201


@app.route('/api/groups/<int:id>', methods=['PUT'])
def update_group(id):
    group = Group.query.get_or_404(id)
    data = request.json
    group.name = data.get('name', group.name)
    group.speciality = data.get('speciality', group.speciality)
    group.course = data.get('course', group.course)
    db.session.commit()
    log_history('update', 'group', id, data)
    return jsonify({'status': 'ok'})


@app.route('/api/groups/<int:id>', methods=['DELETE'])
def delete_group(id):
    group = Group.query.get_or_404(id)
    db.session.delete(group)
    db.session.commit()
    log_history('delete', 'group', id, {})
    return jsonify({'status': 'ok'})


# ============ ПРЕПОДАВАТЕЛИ ============
@app.route('/api/teachers', methods=['GET'])
def get_teachers():
    teachers = Teacher.query.order_by(Teacher.name).all()
    return jsonify([{
        'id': t.id, 'name': t.name, 'short_name': t.short_name, 'color': t.color,
        'subjects': [{'id': s.id, 'name': s.name, 'short_name': s.short_name} for s in t.subjects]
    } for t in teachers])


@app.route('/api/teachers/<int:id>/subjects', methods=['GET'])
def get_teacher_subjects(id):
    teacher = Teacher.query.get_or_404(id)
    return jsonify([{'id': s.id, 'name': s.name, 'short_name': s.short_name} for s in teacher.subjects])


@app.route('/api/teachers', methods=['POST'])
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


@app.route('/api/teachers/<int:id>', methods=['PUT'])
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


@app.route('/api/teachers/<int:id>', methods=['DELETE'])
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    log_history('delete', 'teacher', id, {})
    return jsonify({'status': 'ok'})


# ============ ДИСЦИПЛИНЫ ============
@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    subjects = Subject.query.order_by(Subject.name).all()
    return jsonify([{
        'id': s.id, 'name': s.name, 'short_name': s.short_name, 'lesson_type': s.lesson_type
    } for s in subjects])


@app.route('/api/subjects', methods=['POST'])
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


@app.route('/api/subjects/<int:id>', methods=['PUT'])
def update_subject(id):
    subject = Subject.query.get_or_404(id)
    data = request.json
    subject.name = data.get('name', subject.name)
    subject.short_name = data.get('short_name', subject.short_name)
    subject.lesson_type = data.get('lesson_type', subject.lesson_type)
    db.session.commit()
    log_history('update', 'subject', id, data)
    return jsonify({'status': 'ok'})


@app.route('/api/subjects/<int:id>', methods=['DELETE'])
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    log_history('delete', 'subject', id, {})
    return jsonify({'status': 'ok'})


# ============ КАБИНЕТЫ ============
@app.route('/api/classrooms', methods=['GET'])
def get_classrooms():
    classrooms = Classroom.query.order_by(Classroom.name).all()
    return jsonify([{
        'id': c.id, 'name': c.name, 'type': c.type, 'capacity': c.capacity
    } for c in classrooms])


@app.route('/api/classrooms', methods=['POST'])
def create_classroom():
    data = request.json
    c = Classroom(name=data['name'], type=data.get('type'), capacity=data.get('capacity'))
    db.session.add(c)
    db.session.commit()
    log_history('create', 'classroom', c.id, data)
    return jsonify({'id': c.id}), 201


@app.route('/api/classrooms/<int:id>', methods=['PUT'])
def update_classroom(id):
    c = Classroom.query.get_or_404(id)
    data = request.json
    c.name = data.get('name', c.name)
    c.type = data.get('type', c.type)
    c.capacity = data.get('capacity', c.capacity)
    db.session.commit()
    log_history('update', 'classroom', id, data)
    return jsonify({'status': 'ok'})


@app.route('/api/classrooms/<int:id>', methods=['DELETE'])
def delete_classroom(id):
    c = Classroom.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    log_history('delete', 'classroom', id, {})
    return jsonify({'status': 'ok'})


# ============ ЗАНЯТИЯ ============
@app.route('/api/lessons', methods=['GET'])
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


def check_conflicts(data, exclude_id=None):
    day = data['day']
    w1 = data.get('week1_lesson', 0)
    w2 = data.get('week2_lesson', 0)
    group_id = data['group_id']
    teacher_id = data['teacher_id']
    classroom_id = data.get('classroom_id')

    query = Lesson.query.filter_by(day=day)
    if exclude_id:
        query = query.filter(Lesson.id != exclude_id)

    for lesson in query.all():
        if w1 > 0 and lesson.week1_lesson == w1:
            if lesson.group_id == group_id:
                return f"Группа уже занята в {day}, {w1} пара (1 неделя)"
            if lesson.teacher_id == teacher_id:
                return f"Преподаватель уже занят в {day}, {w1} пара (1 неделя)"
            if classroom_id and lesson.classroom_id == classroom_id:
                return f"Кабинет уже занят в {day}, {w1} пара (1 неделя)"
        if w2 > 0 and lesson.week2_lesson == w2:
            if lesson.group_id == group_id:
                return f"Группа уже занята в {day}, {w2} пара (2 неделя)"
            if lesson.teacher_id == teacher_id:
                return f"Преподаватель уже занят в {day}, {w2} пара (2 неделя)"
            if classroom_id and lesson.classroom_id == classroom_id:
                return f"Кабинет уже занят в {day}, {w2} пара (2 неделя)"
    return None


@app.route('/api/lessons', methods=['POST'])
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


@app.route('/api/lessons/<int:id>', methods=['GET'])
def get_lesson(id):
    l = Lesson.query.get_or_404(id)
    return jsonify({
        'id': l.id, 'group_id': l.group_id, 'teacher_id': l.teacher_id,
        'subject_id': l.subject_id, 'classroom_id': l.classroom_id,
        'day': l.day, 'week1_lesson': l.week1_lesson, 'week2_lesson': l.week2_lesson,
        'lesson_type': l.lesson_type
    })


@app.route('/api/lessons/<int:id>', methods=['PUT'])
def update_lesson(id):
    lesson = Lesson.query.get_or_404(id)
    data = request.json
    # Собираем итоговые данные для проверки конфликта
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


@app.route('/api/lessons/<int:id>', methods=['DELETE'])
def delete_lesson(id):
    lesson = Lesson.query.get_or_404(id)
    db.session.delete(lesson)
    db.session.commit()
    log_history('delete', 'lesson', id, {})
    return jsonify({'status': 'ok'})


@app.route('/api/lessons/clear', methods=['POST'])
def clear_lessons():
    count = Lesson.query.delete()
    db.session.commit()
    log_history('delete', 'lessons', 0, {'count': count})
    return jsonify({'status': 'ok', 'deleted': count})


if __name__ == '__main__':
    app.run(debug=True, port=5000)