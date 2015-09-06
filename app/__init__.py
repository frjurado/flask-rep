##############################
# here goes the app creation #
# and config loading         #
##############################

from flask import Flask
from config import config

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from app.main import main
    app.register_blueprint(main)

    return app
