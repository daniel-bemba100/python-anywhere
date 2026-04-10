import os
from dotenv import load_dotenv
import redis

load_dotenv()

class Config:
    """Application configuration."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-subscribe-chat-key-change-in-prod'
    SESSION_TYPE = 'redis'
    SESSION_REDIS = None  # Set later in app.py
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 min
    
    # Database configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'subscribe_db')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
    
    # SocketIO
    SOCKETIO_ASYNC_MODE = None
    
    # Redis config
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

