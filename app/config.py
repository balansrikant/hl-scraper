import os


class Config:
    DEBUG = False
    # BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or "b'LJO\xe7\xf7\xfft\xc1\x9cf\xfb\xf6K\xcbn\xdf\xebs)\xe2f\x7f\x03\xa4'"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bookstore.sqlite3'