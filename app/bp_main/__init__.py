# -*- coding: utf-8 -*-
from flask import Blueprint
from ..models.users import Permission
from ..helpers import redirect_url
from .. import aside

main = Blueprint('main', __name__, template_folder='templates')

@main.app_context_processor
def inject_permissions():
    return dict(
        Permission = Permission,
        redirect_url = redirect_url,
        aside = aside
    )

from . import views, errors
