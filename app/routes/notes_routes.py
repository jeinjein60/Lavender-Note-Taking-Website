# app/notes/routes.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Note
from app.models import Vote
from config import Config

note_bp = Blueprint('note', __name__)

@note_bp.route('/serve_index')
@login_required
def serve_index():
    return render_template('index.html')

@note_bp.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return jsonify([
        {
            'id': n.id,
            'title': n.title,
            'content': n.content,
            'image_filename': n.image_filename 
        } for n in notes
    ])

@note_bp.route('/api/notes', methods=['POST'])
@login_required
def create_note():
    title = request.form.get('title')
    content = request.form.get('content')
    is_public = True if request.form.get('is_public') == 'on' else False
    image = request.files.get('image')
    image_filename = None

    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        image_filename = filename

    note = Note(
        title=title,
        content=content,
        user_id=current_user.id,
        image_filename=image_filename,
        is_public=is_public 
    )
    note = Note(title=title, content=content, user_id=current_user.id, image_filename=image_filename)
    db.session.add(note)
    db.session.commit()
    return jsonify({'message': 'Note created successfully'})

@note_bp.route('/api/notes/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    data = request.get_json()
    note = Note.query.get_or_404(note_id)
    note.title = data['title']
    note.content = data['content']
    db.session.commit()
    return jsonify({'message': 'updated'})

@note_bp.route('/api/notes/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.image_filename:
        image_path = os.path.join(Config.UPLOAD_FOLDER, note.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'deleted'})

@note_bp.route('/api/notes/public', methods=['GET'])
@login_required
def get_public_notes():
    notes = Note.query.order_by(Note.id.desc()).limit(20).all()
    return jsonify([
        {'title': n.title, 'content': n.content, 'user_id': n.user_id}
        for n in notes
    ])

@property
def vote_count(self):
    up = Vote.query.filter_by(note_id=self.id, vote_type='up').count()
    down = Vote.query.filter_by(note_id=self.id, vote_type='down').count()
    return up - down

@note_bp.route('/api/notes/<int:note_id>/vote', methods=['POST'])
@login_required
def vote_note(note_id):
    vote_type = request.json.get('vote_type')  # "up" or "down"
    existing_vote = Vote.query.filter_by(user_id=current_user.id, note_id=note_id).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            db.session.delete(existing_vote)  # Toggle vote off
        else:
            existing_vote.vote_type = vote_type  # Change vote
    else:
        vote = Vote(user_id=current_user.id, note_id=note_id, vote_type=vote_type)
        db.session.add(vote)

    db.session.commit()
    return jsonify({'message': 'vote updated'})