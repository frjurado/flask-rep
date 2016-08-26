# -*- coding: utf-8 -*-
from flask import Blueprint
from ..models.users import Permission
from ..helpers import redirect_url


main = Blueprint('main', __name__, template_folder='templates')

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

@main.app_context_processor
def inject_redirect():
    return dict(redirect_url=redirect_url)

from . import views, errors
