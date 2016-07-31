import re
from unidecode import unidecode
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, flash, abort, request, redirect, url_for
from flask.ext.login import current_user


def urlize(string):
    """
    Take a Unicode string and:
      * strip special characters,
      * strip symbols,
      * lowercase,
      * substitute whitespace for '-'.
    (for generating url slugs).
    """
    string = unidecode(string)
    string = re.sub(r'[^(\w\s)]', '', string)
    string = string.lower()
    string = re.sub(r'[\s]+', '-', string)
    return string


def serialize(expiration=None):
    return Serializer(current_app.config['SECRET_KEY'], expiration)


def load_token(serializer, token):
    try:
        return serializer.loads(token)
    except:
        return None


def invalid_token(message="Invalid or expired token"):
    flash(message)
    abort(404)


def get_or_404(model, criterion):
    obj = model.query.filter(criterion).first()
    if obj is None:
        abort(404)
    return obj


def next_or_index():
    url = request.args.get('next') or url_for('main.index')
    return redirect(url)


def to_dashboard():
    url = url_for('user.profile', username=current_user.username)
    return redirect(url)

# this stupid thing doesn't work...
# class Redirection(object):
#     def url(self):
#         raise NotImplementedError()
#
#     def __call__(self):
#         return redirect(self.url())
#
#
# class next_or_index(Redirection):
#     def url(self):
#         return request.args.get('next') or url_for('main.index')
#
#
# class to_dashboard(Redirection):
#     def url(self):
#         return url_for('dash.user_profile', username=current_user.username)
