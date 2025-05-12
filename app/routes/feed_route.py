# app/routes/feed_route.py
from flask import Blueprint, render_template, request 
from flask_login import login_required, current_user 
from app.models import Note, User 

main = Blueprint('main', __name__)

@main.route('/feed')
@login_required
def feed():
    notes = Note.query.filter_by(is_public=True).order_by(Note.id.desc()).all()
    return render_template('feed.html', notes=notes)

@main.route('/explore')
@login_required
def explore():
    search_query = request.args.get('query')
    notes = [] # Initialize notes as an empty list
    topic = request.args.get('topic')
    query = Note.query.filter_by(is_public=True)

    if topic:
        query = query.filter(Note.topic == topic)
        notes = query.order_by(Note.id.desc()).all()

    if search_query:
        # Perform a case-insensitive search on note title and content
        notes = Note.query.filter(
            (Note.title.ilike(f'%{search_query}%')) |
            (Note.content.ilike(f'%{search_query}%'))
        ).order_by(Note.created_at.desc()).all()
    else:
        # Display recent notes as a default if no search query
        notes = Note.query.order_by(Note.created_at.desc()).limit(20).all()

    return render_template('explore.html', notes=notes, search_query=search_query)

@main.route('/profile')
@login_required
def profile():
    # Use 'current_user' (with an underscore) as the Flask-Login proxy object
    return render_template('profile.html', user=current_user)