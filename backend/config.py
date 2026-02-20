import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.environ.get("FLASK_ENV")
    ELEVATE_ADMIN_SECRET = os.environ.get("ELEVATE_ADMIN_SECRET")
    DELETE_USER_SECRET = os.environ.get("DELETE_USER_SECRET")
