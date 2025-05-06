from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..models import Task
from app import db


task_bp = Blueprint('tasks', __name__)

@task_bp.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([
        {"id": t.id, "description": t.description, "category": t.category}
        for t in tasks
    ])

@task_bp.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    data = request.get_json()
    task = Task(description=data['description'], category=data['category'], user_id=current_user.id)
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task created", "id": task.id})

@task_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    task.description = data.get('description', task.description)
    db.session.commit()
    return jsonify({"message": "Task updated"})


@task_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})
