from functools import wraps
from flask import current_app, abort, redirect, url_for, flash
from flask.ext.login import current_user
from .models import Permission


def signup_enabled(f):
    """
    Use as a decorator to block signup view if
    'SIGNUP_ENABLED' is set to False.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config['SIGNUP_ENABLED']:
            flash("Signup is disabled.")
            abort(404)
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """
    Use as a decorator to restrict views to logged-out users
    (for login and signup views, for example).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_anonymous:
            flash("You're already logged in.")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def member_required(f):
    """
    Use as a decorator to restrict views to members.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_member():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def confirmation_required(f):
    """
    Use as a decorator to restrict views to confirmed users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.confirmed:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    """
    Use as a decorator for permission-based access to views.
    Argument should be an attribute of Permission class.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Specific permission-based decorator for
    administrator (and main administrator) exclusive views.
    """
    return permission_required(Permission.ADMINISTER)(f)

def admin_or_self_required(f):
    """
    Specific permission-based decorator for
    administrator- or self- exclusive views.
    """
    @wraps(f)
    def decorated_function(username, *args, **kwargs):
        if not current_user.is_administrator() and not current_user.username == username:
            abort(403)
        return f(username, *args, **kwargs)
    return decorated_function

def main_admin_required(f):
    """
    Specific decorator for main administrator-exclusive views.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_main_administrator():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def main_admin_excluded(f): ## ?
    """
    Specific decorator for main administrator-excluded views.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_main_administrator():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
