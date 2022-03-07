from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.sqlite3'
    # app.config['SECRET_KEY'] = "random string"
    
    
    with app.app_context():
        # include our Routes
        from . import routes

    return app
