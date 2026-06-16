import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # PostgreSQL на Render, SQLite локально
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///kitsune.db')
    
    # Render даёт postgres:// но SQLAlchemy нужен postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY  = os.getenv('JWT_SECRET_KEY', 'dev-secret-change-me')
    SECRET_KEY      = os.getenv('SECRET_KEY',     'dev-flask-secret')
    DEBUG           = os.getenv('DEBUG', 'false').lower() == 'true'
    CORS_ORIGINS    = os.getenv('CORS_ORIGINS', '*')
