from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.login import LoginManager
from flask.ext.wtf.csrf import CsrfProtect
from config import config


db = SQLAlchemy()
mail = Mail()
csrf = CsrfProtect()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
# uncomment next line
# if you want to be redirected to auth.login when 401
# login_manager.login_view = 'auth.login'
# and these for fresh logins
# login_manager.refresh_view = 'auth.login'
# login_manager.needs_refresh_message = "Enter your credentials again, please."

def create_app(config_name='default'):
    """
    Application factory.

    Pass in the appropriate configuration as a parameter, either:
        'development' (or 'default'),
        'testing',
        'production'.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .main import main
    from .auth import auth
    from .dash import dash
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(dash, url_prefix='/dashboard')

    return app
