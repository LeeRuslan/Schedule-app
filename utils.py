import json
from extensions import db
from models import HistoryLog, Lesson


def log_history(action, entity_type, entity_id, details):
    log = HistoryLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=json.dumps(details, ensure_ascii=False)
    )
    db.session.add(log)
    db.session.commit()


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