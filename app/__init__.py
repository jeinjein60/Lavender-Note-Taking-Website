from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

login_manager.login_view = 'auth.login'  # Redirect to login if not authenticated

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from .routes.auth_routes import auth_bp
    from .routes.notes_routes import note_bp
    from .routes.admin_routes import admin_bp
    from .routes.task_routes import task_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(note_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(task_bp)

    # Setup user loader
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create tables and add default admin if not exists
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            admin = User(username='admin', password=generate_password_hash('adminpass'), is_admin=True)
            db.session.add(admin)
            db.session.commit()

    return app
