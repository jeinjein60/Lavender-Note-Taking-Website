from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///enrollment.db'
app.secret_key = 'super-secret-key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    tasks = db.relationship('Task', backref='user', lazy=True)
    notes = db.relationship('Note', backref='user', lazy=True)
    theme = db.Column(db.String(20), default="purple")
    avatar_url = db.Column(db.Text, default="https://i.pravatar.cc/100")
    bio = db.Column(db.Text, default="Creative coder & coffee-fueled note taker 🌿")

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filetype = db.Column(db.String(10), nullable=False)  # 'image' or 'video'
    category = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref='uploads')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        category = request.form.get('category', 'Uncategorized')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            ext = filename.rsplit('.', 1)[1].lower()
            filetype = 'image' if ext in ['png', 'jpg', 'jpeg', 'gif'] else 'video'

            new_upload = Upload(
                filename=filename,
                filetype=filetype,
                category=category,
                user_id=current_user.id
            )
            db.session.add(new_upload)
            db.session.commit()

            return redirect(url_for('upload_file'))  # Reload page to show new file

    # On GET (or after POST redirect), show user's uploads
    uploads = Upload.query.filter_by(user_id=current_user.id).all()
    uploads_by_category = {}
    for u in uploads:
        uploads_by_category.setdefault(u.category, []).append(u)

    return render_template('upload.html', uploads_by_category=uploads_by_category)



@app.route('/set_theme/<theme>')
@login_required
def set_theme(theme):
    if theme not in ['light', 'dark', 'purple']:
        return "Invalid theme", 400
    current_user.theme = theme
    db.session.commit()
    return redirect(request.referrer or url_for('index'))


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/homepage')
@login_required
def homepage():
    return render_template('homepage.html')

@app.route('/tasks')
@login_required
def tasks():
    tasks = Task.query.all()
    return render_template('buttons.html', tasks=tasks)

@app.route('/get_tasks')
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    task_data = [{'content': t.content, 'category': t.category} for t in tasks]
    return jsonify(task_data)

@app.route('/delete_category', methods=['POST'])
@login_required
def delete_category():
    data = request.get_json()
    category_key = data.get('category')

    if category_key:
        Task.query.filter_by(user_id=current_user.id, category=category_key).delete()
        db.session.commit()
        return jsonify({'status': 'success'})

    return jsonify({'error': 'Category not found'}), 400




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('dashAdmin.html', users=users)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('usersAdmin.html', users=users)

@app.route('/admin/pages')
@login_required
@admin_required
def admin_pages():
    notes = Note.query.all()
    return render_template('pagesAdmin.html', notes=notes)

@app.route('/admin/pages/delete/<int:note_id>')
@login_required
@admin_required
def delete_note_admin(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    # flash('Note deleted.', 'info')
    return redirect(url_for('admin_pages'))


@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        db.session.commit()
        # flash('User updated.', 'success')
        return redirect(url_for('admin_users'))
    return render_template('editUser.html', user=user)

@app.route('/admin/users/delete/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    # flash('User deleted.', 'info')
    return redirect(url_for('admin_users'))

@app.route('/serve_index')
@login_required
def serve_index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            # flash('Username already exists.', 'warning')
            return redirect(url_for('register'))
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed)
        db.session.add(new_user)
        db.session.commit()
        # flash('Account created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            # flash('Logged in.', 'success')
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('feed'))
        # flash('Invalid credentials.', 'danger')
    return render_template('loginpage.html')

@app.route('/create_task', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    content = data.get('content')
    category = data.get('category')

    if not content or not category:
        return jsonify({'error': 'Missing content or category'}), 400

    new_task = Task(content=content, category=category, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({'message': 'Task saved'})



@app.route('/admin/tasks')
@login_required
def admin_tasks():
    if not current_user.is_admin:
        return redirect(url_for('index'))

    tasks = Task.query.all()

    tasks_by_category = {}
    for task in tasks:
        cat = task.category or "Uncategorized"
        if cat not in tasks_by_category:
            tasks_by_category[cat] = []
        tasks_by_category[cat].append(task)

    return render_template("tasksAdmin.html", tasks_by_category=tasks_by_category)

@app.route('/admin/delete_task/<int:task_id>')
@login_required
def delete_task_admin(task_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))

    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('admin_tasks'))



@app.route('/delete_task', methods=['POST'])
@login_required
def delete_task():
    data = request.get_json()
    content = data.get('content')
    category = data.get('category')

    task = Task.query.filter_by(content=content, category=category, user_id=current_user.id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted'})
    return jsonify({'error': 'Task not found'}), 404


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return jsonify([{'id': n.id, 'title': n.title, 'content': n.content} for n in notes])


@app.route('/api/notes', methods=['POST'])
@login_required
def create_note():
    data = request.get_json()
    n = Note(title=data['title'], content=data['content'], user_id=current_user.id)
    db.session.add(n)
    db.session.commit()
    return jsonify({'message': 'created'}), 201



@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.get_json()
    note = Note.query.get_or_404(note_id)
    note.title, note.content = data['title'], data['content']
    db.session.commit()
    return jsonify({'message': 'updated'})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'deleted'})

@app.route('/feed')
@login_required
def feed():
    return render_template('feed.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()
    avatar_url = data.get('avatar_url')
    bio = data.get('bio')

    if avatar_url:
        current_user.avatar_url = avatar_url
    if bio is not None:
        current_user.bio = bio

    db.session.commit()
    return jsonify({'status': 'success'})


@app.route('/explore')
@login_required
def explore():
    return render_template('explore.html')


with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        hashed = generate_password_hash('adminpass', method='pbkdf2:sha256')
        admin = User(username='admin', password=hashed, is_admin=True)
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
