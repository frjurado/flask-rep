import unittest
import time
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission
from sqlalchemy.exc import IntegrityError


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # passwords
    def test_password_setter(self):
        u = User(email="u@example.com", password="cat")
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(email="u@example.com", password="cat")
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(email="u@example.com", password="cat")
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u1 = User(email="u1@example.com", password="cat")
        u2 = User(email="u2@example.com", password="cat")
        self.assertTrue(u1.password_hash != u2.password_hash)

    # User table integrity
    def test_email_not_nullable(self):
        with self.assertRaises(IntegrityError):
            u = User(password="cat")
            db.session.add(u)
            db.session.commit()

    def test_email_unique(self):
        u1 = User(email="u1@example.com", password="cat")
        db.session.add(u1)
        db.session.commit()
        with self.assertRaises(IntegrityError):
            u2 = User(email="u1@example.com", password="cat")
            db.session.add(u2)
            db.session.commit()

    def test_username_unique(self):
        u1 = User(email="u1@example.com", username="u1", password="cat")
        db.session.add(u1)
        db.session.commit()
        with self.assertRaises(IntegrityError):
            u2 = User(email="u2@example.com", username="u1", password="cat")
            db.session.add(u2)
            db.session.commit()

    # confirmation token
    def test_valid_confirmation_token(self):
        u = User(email="u@example.com", password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(email="u1@example.com", password="cat")
        u2 = User(email="u2@example.com", password="cat")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(email="u@example.com", password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    # password reset token
    # def test_valid_password_reset_token(self):
    #     u = User(email="u@example.com", username="u", password="cat")
    #     db.session.add(u)
    #     db.session.commit()
    #     token = u.generate_reset_token()
    #     user = User.check_reset_token(token)
    #     self.assertTrue(user == u)
    #     user.reset("user", "dog")
    #     self.assertTrue(u.username == "user")
    #     self.assertTrue(u.verify_password("dog"))
    #
    # def test_invalid_password_reset_token(self):
    #     u1 = User(email="u1@example.com", username="u1", password="cat")
    #     u2 = User(email="u2@example.com", username="u2", password="cat")
    #     db.session.add(u1)
    #     db.session.add(u2)
    #     db.session.commit()
    #     token = u1.generate_reset_token()
    #     user = User.check_reset_token(token)
    #     self.assertFalse(user == u2)
    #
    # def test_expired_reset_token(self):
    #     u = User(email="u@example.com", password="cat")
    #     db.session.add(u)
    #     db.session.commit()
    #     token = u.generate_reset_token(1)
    #     time.sleep(2)
    #     self.assertFalse(User.check_reset_token(token))

    # change email
    def test_valid_email_change(self):
        u = User(email="u@example.com", password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token("user@example.com")
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == "user@example.com")

    def test_invalid_email_change(self):
        u1 = User(email="u1@example.com", username="u1", password="cat")
        u2 = User(email="u2@example.com", username="u2", password="cat")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token("user1@example.com")
        self.assertFalse(u2.change_email(token))
        self.assertFalse(u1.email == "user1@example.com")
        self.assertFalse(u2.email == "user1@example.com")

    def test_expired_email_change(self):
        u = User(email="u@example.com", password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token("user1@example.com", 1)
        time.sleep(2)
        self.assertFalse(u.change_email(token))
        self.assertFalse(u.email == "user@example.com")

    # roles and permissions
    def test_roles_and_permissions(self):
        Role.insert_roles()
        # default user
        u = User(email="u@example.com", password="cat")
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.MODERATE))
        # add permission
        permissions = Permission.COMMENT | Permission.ROLE | Permission.MODERATE
        u.role = Role.query.filter_by(permissions=permissions).first()
        self.assertTrue(u.can(Permission.MODERATE))
        # block user
        u.role = Role.query.filter_by(permissions=0).first()
        self.assertFalse(u.can(Permission.COMMENT))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.MODERATE))
