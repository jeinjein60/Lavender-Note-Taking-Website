from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Note

main = Blueprint('main', __name__)

@main.route('/feed')
@login_required
def feed():
    notes = Note.query.order_by(Note.id.desc()).all()
    return render_template('feed.html', notes=notes)
