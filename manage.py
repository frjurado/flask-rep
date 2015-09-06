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

from app import create_app
app = create_app('default')

if __name__ == '__main__':
    app.run()

########################
# To run it:
#
# $ source venv/Scripts/activate
# (venv) $ python manage.py
#
########################
