# app/__init__.py
from flask import Flask, redirect, url_for, render_template # Added render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user # Added current_user
from flask_migrate import Migrate
from config import Config
import os

# Initialize extensions (globally, but without passing the app object yet)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

login_manager.login_view = 'auth.login' # Redirect to login if not authenticated

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions WITH the app object
    # db is now fully configured for use
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # --- CRITICAL ORDERING FOR CIRCULAR IMPORT FIX ---

    # 1. Import Models HERE, AFTER db.init_app(app)
    # This ensures that when models.py does 'from app import db',
    # 'db' is already associated with the app instance.
    from .models import User, Note, Task # Import all your models here

    # 2. Setup user loader HERE (it uses the User model)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 3. Import Blueprints HERE, AFTER models and user_loader
    # Blueprints can now safely import models or db if they need to
    from .routes.auth_routes import auth_bp
    from .routes.notes_routes import note_bp
    from .routes.admin_routes import admin_bp
    from .routes.task_routes import task_bp
    from .routes.feed_route import main # This import is now safe

    # 4. Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(note_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(task_bp)
    app.register_blueprint(main) # Registered the 'main' blueprint

    # 5. Define App-level Routes (like the home route)
    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('note.serve_index')) # Assuming 'note.serve_index' is main page
        else:
            return redirect(url_for('auth.login'))

    # 6. Create tables and add default admin if not exists (within app context)
    with app.app_context():
        db.create_all()
        # Add your admin user creation logic here, if not already present
        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            admin = User(username='admin', password=generate_password_hash('adminpass'), is_admin=True)
            db.session.add(admin)
            db.session.commit()

    return app