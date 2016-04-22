from flask import Blueprint


dash = Blueprint('dash', __name__, template_folder='templates')

from . import views
