########################
# Structured Flask app #
# (blueprint version)  #
########################

# This file retains the app creation and running.
# The basic structure looks somthing like this,
# where '/main' is one blueprint package:
#
# /yourapplication
#   /app
#     __init__.py
#     ...
#     /static
#     /templates
#     /main
#       __init__.py
#       ...
#   /tests
#     __init__.py
#     ...
#   manage.py
#   config.py
#

########################
# Through Flask-Script #
########################

from app import create_app, db
from app.models import Role, User
from flask.ext.script import Manager, Shell

app = create_app('default')
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, Role=Role, User=User)

manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()

########################
# To check available commands:
#
# $ source venv/Scripts/activate
# (venv) $ python manage.py
#
# To run it:
#
# $ source venv/Scripts/activate
# (venv) $ python manage.py runserver
#
########################
