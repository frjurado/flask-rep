# -*- coding: utf-8 -*-
from datetime import datetime as dt
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request
from flask.ext.login import UserMixin, AnonymousUserMixin, current_user
from .. import db, login_manager
from . import BaseModel
from ..helpers import serialize, load_token


class Permission():
    COMMENT    = 0b00000001 # 0x01
    MODERATE   = 0b00000010 # 0x02
    WRITE_POST = 0b00000100 # 0x04
    EDIT_POST  = 0b00001000 # 0x08
    ADMINISTER = 0b10000000 # 0x80


class Role(BaseModel):
    name = db.Column(db.String(128), index=True, unique=True, nullable=False)
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False, index=True)
    # relationship w/ User
    users = db.relationship("User", back_populates="role")

    @classmethod
    def insert_roles(cls):
        roles = {
            "Guest":     (Permission.COMMENT, True),
            "Moderator": (Permission.COMMENT |
                          Permission.MODERATE, False),
            "Writer":    (Permission.COMMENT |
                          Permission.MODERATE |
                          Permission.WRITE_POST, False),
            "Editor":    (Permission.COMMENT |
                          Permission.MODERATE |
                          Permission.WRITE_POST |
                          Permission.EDIT_POST, False),
            "Administrator": (0xff, False) # omnipotent
        }
        for r in roles:
            role = cls.query.filter_by(name=r).first()
            if role is None:
                role = cls(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class User(UserMixin, BaseModel):
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    username = db.Column(db.String(128), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), unique=True)
    avatar_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime, default=dt.utcnow)
    # relationship w/ Role
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    role = db.relationship("Role", back_populates="users")
    # relationship w/ content.py models
    posts = db.relationship("Post", backref="author")
    #
    _endpoint = "main.author"

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        self._set_avatar_hash()

    def _get_name(self):
        return self.name or self.username

    def _href(self):
        return url_for(self._endpoint, username=self.username)

    #password
    @property
    def password(self):
        raise AttributeError(u"password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #avatar
    def _set_avatar_hash(self):
        self.avatar_hash = md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=64, default="mm", rating="g"):
        if request.is_secure:
            url = "https://secure.gravatar.com/avatar"
        else:
            url = "http://www.gravatar.com/avatar"
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(
            url = url,
            hash = self.avatar_hash,
            size = size,
            default = default,
            rating = rating
        )

    # tokens
    def generate_confirmation_token(self, expiration=3600):
        s = serialize(expiration)
        return s.dumps({'confirm': self.id})

    def generate_email_change_token(self, new_email, expiration=3600):
        s = serialize(expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def generate_reset_token(self, expiration=3600):
        s = serialize(expiration)
        return s.dumps({'reset': self.id})

    def confirm(self, token):
        s = serialize()
        data = load_token(s, token)
        if data is None or data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def change_email(self, token):
        s = serialize()
        data = load_token(s, token)
        if data is None or data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None \
                or self.query.filter_by(email=new_email).first() is not None: # self.query?
            return False
        self.email = new_email
        self._set_avatar_hash()
        db.session.add(self)
        return True

    def reset(self, new_username, new_password): # checking is done within the form
        self.username = new_username
        self.password = new_password
        db.session.add(self)

    # roles
    def get_role(self):
        return self.role.name

    def set_role(self, role_id):
        role = Role.query.get(int(role_id))
        if role is None \
                or role == self.role \
                or ( self == current_user and self.is_administrator() ):
            return False
        self.role = role
        db.session.add(self)
        return True

    def can(self, permissions):
        return (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    #generate fake users
    @classmethod
    def generate_fake(cls, count=32):
        from random import seed
        import forgery_py
        from sqlalchemy.exc import IntegrityError

        seed()
        for i in range(count):
            u = cls(email = forgery_py.internet.email_address(),
                    username = forgery_py.internet.user_name(True),
                    password = forgery_py.lorem_ipsum.word(),
                    name = forgery_py.name.full_name(),
                    confirmed = True,
                    member_since = forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class AnonymousUser(AnonymousUserMixin):
    email = None
    username = None
    name = None
    confirmed = False

    def get_role(self):
        return None

    def can(self, permissions):
        return (Permission.COMMENT & permissions) == permissions

    def is_administrator(self):
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.anonymous_user = AnonymousUser
