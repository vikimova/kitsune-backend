import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///kitsune.db')
    
    # Railway даёт postgres://, меняем на postgresql+pg8000://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+pg8000://', 1)
    elif DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+pg8000://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret')
    SECRET_KEY     = os.getenv('SECRET_KEY', 'dev-flask-secret')
    DEBUG          = os.getenv('DEBUG', 'false').lower() == 'true'
    CORS_ORIGINS   = os.getenv('CORS_ORIGINS', '*')
