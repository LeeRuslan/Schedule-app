from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

teacher_subjects = db.Table('teacher_subjects',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    speciality = db.Column(db.String(100))
    course = db.Column(db.Integer)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    color = db.Column(db.String(20), default='#3b82f6')
    subjects = db.relationship('Subject', secondary=teacher_subjects, backref='teachers')

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    lesson_type = db.Column(db.String(20), default='Лекция')

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    type = db.Column(db.String(50))
    capacity = db.Column(db.Integer)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'))
    day = db.Column(db.String(20), nullable=False)
    week1_lesson = db.Column(db.Integer, default=0)
    week2_lesson = db.Column(db.Integer, default=0)
    lesson_type = db.Column(db.String(20), default='Лекция')

    group = db.relationship('Group')
    teacher = db.relationship('Teacher')
    subject = db.relationship('Subject')
    classroom = db.relationship('Classroom')

class HistoryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.Column(db.String(50), default='admin')
    action = db.Column(db.String(20))
    entity_type = db.Column(db.String(20))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)