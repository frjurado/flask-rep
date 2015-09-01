import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "83oG69H1D11RBF7tEq75qU25oEA1mxmM"


class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
