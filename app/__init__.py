from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите, чтобы продолжить.'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    # Импорт моделей для создания таблиц
    from app import models
    with app.app_context():
        db.create_all()

    # Регистрация blueprints
    from app.auth import auth_bp
    from app.routes import main_bp
    from app.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app