########################
# Structured Flask app #
#   (simple version)   #
########################

# This file retains the app running only.
# Details apart, any sensible project
# should adhere to this basic structure:
#
# /yourapplication
#   /app
#     __init__.py
#     ...
#     /static
#     /templates
#   /tests
#     __init__.py
#     ...
#   manage.py
#   config.py
#

from app import app

if __name__ == '__main__':
    app.run(debug=True)

########################
# To run it:
#
# $ source venv/Scripts/activate
# (venv) $ python manage.py
#
########################
