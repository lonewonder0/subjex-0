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

def create_app(test_config=None):
    app = Flask(__name__, static_folder='../frontend/out')
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

    db.init_app(app)
    login_manager.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
    
    return app
