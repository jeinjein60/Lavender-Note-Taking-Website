from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app import db
from ..models import User, Note

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('dashAdmin.html', users=users)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('usersAdmin.html', users=users)

@admin_bp.route('/admin/pages')
@login_required
@admin_required
def admin_pages():
    notes = Note.query.all()
    return render_template('pagesAdmin.html', notes=notes)

@admin_bp.route('/admin/pages/delete/<int:note_id>')
@login_required
@admin_required
def delete_note_admin(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted.', 'info')
    return redirect(url_for('admin.admin_pages'))

@admin_bp.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        if request.form['password']:
            from werkzeug.security import generate_password_hash
            user.password = generate_password_hash(request.form['password'])
        db.session.commit()
        flash('User updated.', 'success')
        return redirect(url_for('admin.admin_users'))
    return render_template('editUser.html', user=user)

@admin_bp.route('/admin/users/delete/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'info')
    return redirect(url_for('admin.admin_users'))
