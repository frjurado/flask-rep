from flask import \
    request, session, render_template, redirect, url_for, flash, current_app
from flask.ext.login import login_required
from . import main
from .. import db
from ..models import User, Role
from ..email import send_email


@main.route('/', methods=['GET', 'POST'])
def index():
    """
    Simple index view.
    To be deprecated, of course.
    """
    users = User.query.all()
    return render_template('index.html', users=users)
