import datetime
import os

app_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A SECRET KEY'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=365)


class DevelopementConfig(BaseConfig):
    HOST = '127.0.0.1'
    PORT = 8080
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORD_QUERIES = True
    SESSION_PERMANENT = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SESSION_TYPE = "filesystem"


class ProductionConfig(BaseConfig):
    DEBUG = False
    host = '0.0.0.0'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORD_QUERIES = True
    SESSION_PERMANENT = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SESSION_TYPE = "filesystem"