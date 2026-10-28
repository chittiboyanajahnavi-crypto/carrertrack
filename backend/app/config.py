import os
import ssl
from datetime import timedelta
from dotenv import load_dotenv

import urllib.parse

# Load .env file from backend root if it exists
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
env_path = os.path.join(backend_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)


class Config:
    """Base application configuration with secure defaults."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'careertrack-dev-secret-key-replace-in-prod')
    
    # Database Settings
    DB_USER = os.environ.get('DB_USER', 'careertrack_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'careertrack_db')

    _encoded_password = urllib.parse.quote_plus(DB_PASSWORD) if DB_PASSWORD else ''
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"mysql+pymysql://{DB_USER}:{_encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
        'pool_size': 10,
        'max_overflow': 20,
    }

    # Set Aiven's CA certificate in DB_SSL_CA to verify TLS for hosted MySQL.
    DB_SSL_CA = os.environ.get('DB_SSL_CA', '').strip()
    if DB_SSL_CA:
        SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = {
            'ssl': ssl.create_default_context(cadata=DB_SSL_CA)
        }

    # Session & Cookie Security (HTTP-only)
    SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME', 'careertrack_session')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 86400))
    )

    # CORS
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    TESTING = True
    # In tests, default to an in-memory SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///:memory:')
    SQLALCHEMY_ENGINE_OPTIONS = {}
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
