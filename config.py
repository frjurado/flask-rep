# -*- coding: utf-8 -*-
import os
from datetime import datetime


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base configuration class. Use child classes.
    """
    NOT_SO_SECRET_KEY = 'pFeZmuXj6t1cZP70gnNS7IS4zhdRvwY7' # don't use this!
    SECRET_KEY = os.environ.get('SECRET_KEY') or NOT_SO_SECRET_KEY
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') # sender
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = u"[Test blog mail] - " # revise
    ADMIN = os.environ.get('ADMIN') # main administrator mail

    SIGNUP_ENABLED = True
    POSTS_PER_PAGE = 10

    UPLOADS_DEFAULT_DEST = './app/static/uploads'
    UPLOADS_DEFAULT_URL = '/static/uploads/'

    COMMENT_MAX_DEPTH = 2

    ORIGIN = datetime(2016, 8, 20, 12, 00, 00, 000000)

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """
    Development configuration class.
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    """
    Testing configuration class.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    """
    Production configuration class.
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SIGNUP_ENABLED = os.environ.get('SIGNUP_ENABLED') or False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
