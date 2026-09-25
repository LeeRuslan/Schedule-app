from flask import Blueprint, request, jsonify
from extensions import db
from models import Classroom
from utils import log_history

classrooms_bp = Blueprint('classrooms', __name__, url_prefix='/api/classrooms')


@classrooms_bp.route('', methods=['GET'])
def get_classrooms():
    classrooms = Classroom.query.order_by(Classroom.name).all()
    return jsonify([{
        'id': c.id, 'name': c.name, 'type': c.type, 'capacity': c.capacity
    } for c in classrooms])


@classrooms_bp.route('', methods=['POST'])
def create_classroom():
    data = request.json
    c = Classroom(
        name=data['name'],
        type=data.get('type'),
        capacity=data.get('capacity')
    )
    db.session.add(c)
    db.session.commit()
    log_history('create', 'classroom', c.id, data)
    return jsonify({'id': c.id}), 201


@classrooms_bp.route('/<int:id>', methods=['PUT'])
def update_classroom(id):
    c = Classroom.query.get_or_404(id)
    data = request.json
    c.name = data.get('name', c.name)
    c.type = data.get('type', c.type)
    c.capacity = data.get('capacity', c.capacity)
    db.session.commit()
    log_history('update', 'classroom', id, data)
    return jsonify({'status': 'ok'})


@classrooms_bp.route('/<int:id>', methods=['DELETE'])
def delete_classroom(id):
    c = Classroom.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    log_history('delete', 'classroom', id, {})
    return jsonify({'status': 'ok'})