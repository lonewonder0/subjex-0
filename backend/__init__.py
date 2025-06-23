from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config 
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Unauthorized, this is a protected route. Please log in."}), 401

@login_manager.user_loader
def load_user(user_id):
  from .models import User
  return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__, static_folder='../frontend/out')
    app.config.from_object(Config)

    CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

    db.init_app(app)
    login_manager.init_app(app)
    
    with app.app_context():
        
        from . import routes
        # Optionally, create tables if they don't exist
        db.create_all()
    
    return app
