from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Note

main = Blueprint('main', __name__)

@main.route('/feed')
@login_required
def feed():
    notes = Note.query.order_by(Note.id.desc()).all()
    return render_template('feed.html', notes=notes)

@main.route('/explore')
@login_required
def explore():
    # You can customize what to display here.
    # For example, you might fetch public notes, trending notes, etc.
    # For now, it's a placeholder.
    # Example: notes = Note.query.filter_by(is_public=True).order_by(Note.created_at.desc()).all()
    return render_template('explore.html') # Pass notes if you fetch them: , notes=notes)

@main.route('/profile')
@login_required
def profile():
    # Flask-Login makes the current_user object available
    # You can pass it to the template to display user-specific information
    return render_template('profile.html', user=current_user)