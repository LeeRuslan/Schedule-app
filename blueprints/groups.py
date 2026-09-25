from flask import Blueprint, request, jsonify
from extensions import db
from models import Group
from utils import log_history

groups_bp = Blueprint('groups', __name__, url_prefix='/api/groups')


@groups_bp.route('', methods=['GET'])
def get_groups():
    groups = Group.query.order_by(Group.name).all()
    return jsonify([{
        'id': g.id, 'name': g.name,
        'speciality': g.speciality, 'course': g.course
    } for g in groups])


@groups_bp.route('', methods=['POST'])
def create_group():
    data = request.json
    group = Group(
        name=data['name'],
        speciality=data.get('speciality'),
        course=data.get('course')
    )
    db.session.add(group)
    db.session.commit()
    log_history('create', 'group', group.id, data)
    return jsonify({'id': group.id}), 201


@groups_bp.route('/<int:id>', methods=['PUT'])
def update_group(id):
    group = Group.query.get_or_404(id)
    data = request.json
    group.name = data.get('name', group.name)
    group.speciality = data.get('speciality', group.speciality)
    group.course = data.get('course', group.course)
    db.session.commit()
    log_history('update', 'group', id, data)
    return jsonify({'status': 'ok'})


@groups_bp.route('/<int:id>', methods=['DELETE'])
def delete_group(id):
    group = Group.query.get_or_404(id)
    db.session.delete(group)
    db.session.commit()
    log_history('delete', 'group', id, {})
    return jsonify({'status': 'ok'})