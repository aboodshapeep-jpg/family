import os

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
    DEBUG = False
    TESTING = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = 'development'

class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    ENV = 'testing'

class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = 'production'