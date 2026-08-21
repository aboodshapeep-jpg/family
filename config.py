import os
from datetime import timedelta

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///family.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Admin email (You - the administrator)
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@familyplatform.com')

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = 'development'
    SESSION_COOKIE_SECURE = False  # Allow non-HTTPS in development
    SQLALCHEMY_ECHO = True

class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    ENV = 'testing'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = 'production'
    SESSION_COOKIE_SECURE = True
    
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
