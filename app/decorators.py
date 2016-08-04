from functools import wraps
from flask import current_app, abort, redirect, url_for, flash
from flask.ext.login import current_user
from .models.users import Permission
from .models.content import Post


def signup_enabled(f):
    """
    Use as a decorator to block signup view if
    SIGNUP_ENABLED is set to False.
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


#   * * *

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


def self_required(f):
    """
    Specific permission-based decorator
    for self-exclusive views.
    """
    @wraps(f)
    def decorated_function(username, *args, **kwargs):
        if current_user.username != username:
            abort(403)
        return f(username, *args, **kwargs)
    return decorated_function


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


# def editor_or_self_required(f):
#     """
#     Specific permission-based decorator for
#     editor- or 'your post'- exclusive views.
#     """
#     @wraps(f)
#     def decorated_function(slug, *args, **kwargs):
#         post = Post.query.filter_by(slug=slug).first()
#         if post is None:
#             abort(404)
#         if not current_user.can(Permission.EDIT_POST) \
#                 and not current_user == post.author:
#             abort(403)
#         return f(slug, post, *args, **kwargs)
#     return decorated_function
