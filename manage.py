import os
from app import create_app, db
from app.models import Permission, Role, User, AnonymousUser
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(
        app=app,
        db=db,
        Permission=Permission,
        Role=Role,
        User=User,
        AnonymousUser=AnonymousUser
    )

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()

#######################################
# To check available commands:        #
#                                     #
# $ source venv/Scripts/activate      #
# (venv) $ python manage.py           #
#                                     #
# To run:                             #
#                                     #
# $ source venv/Scripts/activate      #
# (venv) $ python manage.py runserver #
#                                     #
#######################################
