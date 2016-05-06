from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask.ext.login import UserMixin, AnonymousUserMixin
from sqlalchemy.ext.declarative import declared_attr
from markdown import markdown
import bleach
from . import db, login_manager
from helpers import urlize


class Permission:
    COMMENT    = 0b00000001 # 0x01
    ROLE       = 0b00000010 # 0x02
    MODERATE   = 0b00000100 # 0x04
    WRITE_POST = 0b00001000 # 0x08
    EDIT_POST  = 0b00010000 # 0x10
    ADMINISTER = 0b10000000 # 0x80


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    member = db.Column(db.Boolean, default=True)
    permissions = db.Column(db.Integer)
    # backref
    users = db.relationship('User', backref='role', lazy='dynamic')

    # string representation
    def __repr__(self):
        return '<Role {0}>'.format(self.name)

    # loading the roles
    @staticmethod
    def insert_roles():
        roles = { 'Blocked': (0x00, False, False),            # 0x00
                  'Guest': (Permission.COMMENT, False, True), # 0x01
                  'Candidate': (Permission.COMMENT |          # 0x03
                                Permission.ROLE,
                                True, False),
                  'Moderator': (Permission.COMMENT |          # 0x07
                                Permission.ROLE |
                                Permission.MODERATE,
                                True, False),
                  'Writer': (Permission.COMMENT |             # 0x0f
                             Permission.ROLE |
                             Permission.MODERATE |
                             Permission.WRITE_POST,
                             True, False),
                  'Editor': (Permission.COMMENT |             # 0x1f
                             Permission.ROLE |
                             Permission.MODERATE |
                             Permission.WRITE_POST |
                             Permission.EDIT_POST,
                             True, False),
                  'Administrator': (0xff, True, False),       # 0xff & 0xfd
                  'Main Administrator': (0xff & ~ Permission.ROLE, True, False) }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.default = roles[r][2]
            role.member = roles[r][1]
            role.permissions = roles[r][0]
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    # registered users only
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    # extra information
    name = db.Column(db.String(64))
    url = db.Column(db.String(128))
    avatar_hash = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    newsletter = db.Column(db.Boolean, default=False)
    # FK to roles
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # backrefs
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xfd).first()
            elif self.username is not None:
                self.role = Role.query.filter_by(permissions=0x03).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        if self.email:
            self.set_avatar_hash()

    # string representation
    def __repr__(self):
        return '<User {0}>'.format(self.username)

    # generate fake
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(
                email=forgery_py.internet.email_address(),
                username=forgery_py.internet.user_name(True),
                password=forgery_py.lorem_ipsum.word(),
                confirmed=True,
                name=forgery_py.name.full_name(),
                member_since=forgery_py.date.date(True)
            )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


    # passwords
    # ---------
    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    # token generation and checking
    # -----------------------------
    def _serialize(self, expiration=None):
        return Serializer(current_app.config['SECRET_KEY'], expiration)

    def generate_confirmation_token(self, expiration=3600):
        s = self._serialize(expiration)
        return s.dumps({'confirm': self.id})

    def generate_email_change_token(self, new_email, expiration=3600):
        s = self._serialize(expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def generate_reset_token(self, expiration=3600):
        s = self._serialize(expiration)
        return s.dumps({'reset': self.id})

    def confirm(self, token):
        s = self._serialize()
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def change_email(self, token):
        s = self._serialize()
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.set_avatar_hash()
        db.session.add(self)
        return True

    # As this one implies a POST, all the checking is done within the form
    def reset(self, new_username, new_password):
        self.username = new_username
        self.password = new_password
        db.session.add(self)


    # gravatar
    # --------
    def set_avatar_hash(self):
        self.avatar_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return self.avatar_hash

    def gravatar(self, size=100, default="mm", rating="g"):
        if request.is_secure:
            url = "https://secure.gravatar.com/avatar"
        else:
            url = "http://www.gravatar.com/avatar"
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(
            url=url,
            hash=self.avatar_hash,
            size=size,
            default=default,
            rating=rating
        )


    # refresh last_seen (before_app_request)
    # --------------------------------------
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)


    # check role, permissions or membership
    # -------------------------------------
    def get_role(self):
        return self.role.name or None

    def can(self, permissions):
        return (self.role.permissions & permissions) == permissions

    def is_member(self):
        return self.role.member

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def is_main_administrator(self):
        return self.can(Permission.ADMINISTER) and not self.can(Permission.ROLE)


    # assign roles, block, unblock, admit and banish
    # ----------------------------------------------
    def _role(self, role):
        self.role = role
        db.session.add(self)
        return True

    def block(self):
        if self.is_member():
            return False
        return self._role(Role.query.filter_by(permissions=0x00).first())

    def unblock(self):
        if self.is_member():
            return False
        return self._role(Role.query.filter_by(permissions=0x01).first())

    def set_role(self, role):
        if not self.can(Permission.ROLE) or not self.confirmed:
            return False
        return self._role(role)

    def admit(self):
        if not self.role.permissions == 0x01:
            return False
        return self._role(Role.query.filter_by(permissions=0x03).first())

    def banish(self):
        if not self.is_member() or self.is_main_administrator():
            return False
        return self._role(Role.query.filter_by(permissions=0x01).first())


class AnonymousUser(AnonymousUserMixin):
    email = None
    username = None
    confirmed = False

    def get_role(self):
        return None

    def can(self, permissions):
        return (Permission.COMMENT & permissions) == permissions

    def is_member(self):
        return False

    def is_administrator(self):
        return False

    def is_main_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CONTENT #
###############################################################################

def post_slug(context):
    slug = urlize(context.current_parameters['name'])
    similar_posts = Post.query.filter(Post.slug.like("{}%".format(slug))).count()
    if similar_posts > 0:
        slug = "{0}-{1}".format(slug, str(similar_posts + 1))
    return slug

# MIXINS
class MainContentMixin(object):
    created = db.Column(db.DateTime(), default=datetime.utcnow) # index?
    modified = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.Boolean, default=False)

    @declared_attr
    def author_id(cls):
        return db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class NameMixin(object):
    name = db.Column(db.String(128))
    slug = db.Column(db.String(128), default=post_slug, onupdate=post_slug)
    excerpt = db.Column(db.Text)


class ContentMixin(object):
    body_md = db.Column(db.Text)
    body_html = db.Column(db.Text)

    # md to html
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        tags = [ 'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em',
            'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p' ]
        target.body_html = bleach.linkify(
            bleach.clean(
                markdown(value, output_format='html'),
                tags=tags,
                strip=True
            )
        )

# BASE CLASS
class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'menu_items',
        'polymorphic_on': type
    }


# HierarchicalMixin is still... missing!
class Post(MainContentMixin, NameMixin, ContentMixin, MenuItem):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), primary_key=True)

    page = db.Column(db.Boolean, default=False)
    comment_enabled = db.Column(db.Boolean, default=True)
    comment_count = db.Column(db.Integer, default=0)

    __mapper_args__ = {
        'polymorphic_identity': 'posts'
    }

    # string representation
    def __repr__(self):
        return '<Post {0}>'.format(self.name)

    # generate fake
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()

        users = [user for user in User.query.all() if user.can(Permission.WRITE_POST)]
        user_count = len(users)
        for i in range(count):
            u = users[randint(0, user_count-1)]
            p = Post(
                name=forgery_py.lorem_ipsum.title(),
                excerpt=forgery_py.lorem_ipsum.paragraph(),
                body_md=forgery_py.lorem_ipsum.paragraphs(3),
                status=True,
                author=u
            )
            db.session.add(p)
            db.session.commit()

db.event.listen(Post.body_md, 'set', Post.on_changed_body)
