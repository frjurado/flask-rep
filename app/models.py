from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request, Markup, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin, current_user
from sqlalchemy.orm import backref ##
from sqlalchemy.ext.declarative import declared_attr
from markdown import markdown
import bleach
from . import db, login_manager
from helpers import urlize, serialize, load_token


class Permission:
    COMMENT    = 0b00000001 # 0x01
    MODERATE   = 0b00000010 # 0x02
    WRITE_POST = 0b00000100 # 0x04
    EDIT_POST  = 0b00001000 # 0x08
    ADMINISTER = 0b10000000 # 0x80


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    # relationships
    users = db.relationship('User', back_populates='role')

    # string representation
    def __repr__(self):
        return '<Role {0}>'.format(self.name)

    # loading the roles
    @staticmethod
    def insert_roles():
        roles = { 'Guest':     (Permission.COMMENT, True),
                  'Moderator': (Permission.COMMENT |
                                Permission.MODERATE, False),
                  'Writer':    (Permission.COMMENT |
                                Permission.MODERATE |
                                Permission.WRITE_POST, False),
                  'Editor':    (Permission.COMMENT |
                                Permission.MODERATE |
                                Permission.WRITE_POST |
                                Permission.EDIT_POST, False),
                  'Administrator': (0xff, False)
                }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.default = roles[r][1]
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
    # FK to roles and relationship
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role', back_populates='users')
    # other relationships
    posts = db.relationship('Post', backref='author')
    tags = db.relationship('Tag', backref='author')
    categories = db.relationship('Category', backref='author')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
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
            u = User( email=forgery_py.internet.email_address(),
                      username=forgery_py.internet.user_name(True),
                      password=forgery_py.lorem_ipsum.word(),
                      confirmed=True,
                      name=forgery_py.name.full_name(),
                      member_since=forgery_py.date.date(True) )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    # passwords
    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # token generation and checking
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
                or self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.set_avatar_hash()
        db.session.add(self)
        return True

    def reset(self, new_username, new_password): #Checking within the form
        self.username = new_username
        self.password = new_password
        db.session.add(self)

    # gravatar
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

    # roles
    def get_role(self):
        return self.role.name

    def set_role(self, role_id):
        role = Role.query.get(int(role_id))
        if role is None or role == self.role \
                or ( self == current_user and self.is_administrator() ):
            return False
        self.role = role
        db.session.add(self)
        return True

    def can(self, permissions):
        return (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)


class AnonymousUser(AnonymousUserMixin):
    email = None
    username = None
    confirmed = False

    def get_role(self):
        return None

    def can(self, permissions):
        return (Permission.COMMENT & permissions) == permissions

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CONTENT #
###############################################################################

# MIXINS
class MainContentMixin(object):
    created = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    modified = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.Boolean, default=False)

    @declared_attr
    def author_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('users.id'),
            default = current_user._get_current_object() # this doesn't work?
        )


class NameMixin(object):
    name = db.Column(db.String(128))
    slug = db.Column(db.String(128))
    excerpt = db.Column(db.Text)
    _endpoint = None

    def href(self):
        if self._endpoint is not None:
            return url_for(self._endpoint, slug=self.slug)
        else:
            return "#"

    def link(self, classes=None):
        return Markup("<a class='{2}' href={0}>{1}</a>".format(
            self.href(),
            self.name,
            classes or ""
        ))

    @staticmethod
    def on_changed_name(target, value, oldvalue, initiator):
        if value != oldvalue:
            base_slug = urlize(value)
            slug = base_slug
            i = 1
            while True:
                if Post.query.filter_by(slug = slug).first() is None:
                    target.slug = slug
                    break
                i = i + 1
                slug = "{}-{}".format(base_slug, i)


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


class HierarchicalMixin(object):
    @declared_attr
    def parent_id(cls):
        fk = '{}.id'.format(cls.__tablename__)
        return db.Column(db.Integer, db.ForeignKey(fk))

    @declared_attr
    def children(cls):
        return db.relationship(
            cls.__name__,
            backref = db.backref('parent', remote_side=cls.id),
            foreign_keys = cls.parent_id # necesary, but don't know why!
        )

    def tree(self, linked=True): # this seems (...) to work! revise!!
        e = self
        tree_list = [e]
        while e.parent is not None:
            e = self.__class__.query.get(e.parent_id)
            tree_list = [e] + tree_list
        if linked:
            output = " > ".join([e.link() for e in tree_list])
        else:
            output = " > ".join([e.name for e in tree_list])
        return Markup(output)

    order = db.Column(db.Integer) # is this necessary?


# BASE CLASS
class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'menu_items',
        'polymorphic_on': type
    }


# many-to-many relationships
post_tag = db.Table(
    'post_tag',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)

# HierarchicalMixin is still missing!
class Post(MainContentMixin, NameMixin, ContentMixin, MenuItem):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), primary_key=True)

    page = db.Column(db.Boolean, default=False)
    comment_enabled = db.Column(db.Boolean, default=True)
    comment_count = db.Column(db.Integer, default=0)
    _endpoint = 'main.post'

    tags = db.relationship(
        'Tag',
        secondary = post_tag,
        back_populates = 'posts'
    )
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('Category', backref='posts', foreign_keys=[category_id])

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
            p = Post( name=forgery_py.lorem_ipsum.title(),
                      excerpt=forgery_py.lorem_ipsum.paragraph(),
                      body_md=forgery_py.lorem_ipsum.paragraphs(3),
                      status=True,
                      author=u )
            db.session.add(p)
            db.session.commit()

    # def edit_link, delete_link, ...
    def edit_link(self):
        href = url_for('post.edit', slug=self.slug)
        link = '<a class="btn btn-primary" href="{}">Edit</a>'.format(href)
        return Markup(link)

    def delete_form(self):
        from .post.forms import DeletePostForm
        form = DeletePostForm(self)
        return form()


class Tag(MainContentMixin, NameMixin, MenuItem):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), primary_key=True)

    _endpoint = 'main.tag'

    posts = db.relationship(
        'Post',
        secondary = post_tag,
        back_populates = 'tags'
    )

    __mapper_args__ = {
        'polymorphic_identity': 'tags'
    }

    # string representation
    def __repr__(self):
        return '<Tag {0}>'.format(self.name)


class Category(MainContentMixin, NameMixin, HierarchicalMixin, MenuItem):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), primary_key=True)

    _endpoint = 'main.category'

    __mapper_args__ = {
        'polymorphic_identity': 'categories'
    }

    # string representation
    def __repr__(self):
        return '<Category {0}>'.format(self.name)

    # def tree(self):
    #     c = self
    #     categories = [c]
    #     while c.parent_id is not None:
    #         c = Category.query.get(c.parent_id)
    #         categories = [c] + categories
    #     return " > ".join([c.name for c in categories])

db.event.listen(Post.body_md, 'set', Post.on_changed_body)
db.event.listen(Post.name, 'set', Post.on_changed_name)
db.event.listen(Tag.name, 'set', Tag.on_changed_name)
db.event.listen(Category.name, 'set', Category.on_changed_name)
