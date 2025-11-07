from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# create database object globally
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # call to initialize extension
    db.init_app(app)
    
    # import blueprints from modules
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    
    return app
