import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'super-secret-key'  # change this in production
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'enrollment.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')