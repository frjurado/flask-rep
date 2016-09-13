# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.login import LoginManager
from flask.ext.wtf.csrf import CsrfProtect
from flask.ext.pagedown import PageDown
from flask.ext.uploads import (UploadSet, IMAGES,
                               configure_uploads, patch_request_class)
from config import config


moment = Moment()
db = SQLAlchemy()
mail = Mail()
csrf = CsrfProtect()
pagedown = PageDown()
images = UploadSet('images', IMAGES)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
# uncomment if you want to be redirected to auth.login when 401
# login_manager.login_view = 'auth.login'
#
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

    moment.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    pagedown.init_app(app)
    configure_uploads(app, images)
    patch_request_class(app, size = 2*1024*1024)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .bp_main import main
    from .bp_auth import auth
    from .bp_user import user
    from .bp_post import post
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(post, url_prefix='/post')

    return app
