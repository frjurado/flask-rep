from datetime import datetime as dt
from bleach import linkify, clean
from markdown import markdown
from flask import url_for, Markup
from flask.ext.login import current_user
from sqlalchemy.ext.declarative import declared_attr
from . import BaseModel
from .users import Permission, Role, User
from .. import db
from ..helpers import urlize


# MIXINS
###########################################################
class MainContentMixin(object):
    created = db.Column(db.DateTime(), default=dt.utcnow, index=True)
    modified = db.Column(db.DateTime, default=dt.utcnow, onupdate=dt.utcnow)
    status = db.Column(db.Boolean, default=False)


class AuthorMixin(object):
    @declared_attr
    def author_id(cls):
        return db.Column(db.Integer,
                         db.ForeignKey("user.id"),
                         default = current_user._get_current_object())


class NameMixin(object):
    name = db.Column(db.String(128), index=True, unique=True, nullable=False)
    slug = db.Column(db.String(128), index=True, unique=True, nullable=False)
    _endpoint = None

    def _href(self):
        if self._endpoint is None:
            raise NotImplementedError("you must define an _endpoint")
        return url_for(self._endpoint, slug=self.slug)

    @classmethod
    def on_changed_name(cls, target, value, oldvalue, initiator):
        if value != oldvalue:
            base_slug = urlize(value)
            slug = base_slug
            i = 1
            while True:
                if cls.query.filter_by(slug=slug).first() is None:
                    target.slug = slug
                    break
                i = i + 1
                slug = "{0}-{1}".format(base_slug, i)


class BodyMixin(object):
    body_md = db.Column(db.Text)
    body_html = db.Column(db.Text)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        tags = [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i',
            'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p'
        ]
        target.body_html = linkify(clean(markdown(value,
                                                  output_format='html'),
                                         tags = tags,
                                         strip = True))


# MANY_TO_MANY
###########################################################
post_tag = db.Table(
    "post_tag",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"))
)

post_image = db.Table(
    "post_image",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("image_id", db.Integer, db.ForeignKey("image.id"))
)


# CLASSES
###########################################################
class MenuItem(BaseModel):
    item_type = db.Column(db.String(128), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "menuitem",
        "polymorphic_on": item_type
    }


class Post(MainContentMixin, NameMixin, BodyMixin, AuthorMixin, MenuItem):
    id = db.Column(db.Integer, db.ForeignKey('menuitem.id'), primary_key=True)
    excerpt = db.Column(db.Text)
    page = db.Column(db.Boolean, default=False)
    comment_enabled = db.Column(db.Boolean, default=True)
    comment_count = db.Column(db.Integer, default=0)
    # relationship w/ Category
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    category = db.relationship("Category",
                               backref = "posts",
                               foreign_keys = category_id)
    # relationship w/ Tag
    tags = db.relationship("Tag",
                           secondary = post_tag,
                           back_populates = "posts")
    # relationship(s) w/ Image
    images = db.relationship("Image",
                             secondary = post_image,
                             back_populates = "posts")
    main_image_id = db.Column(db.Integer, db.ForeignKey("image.id"))
    main_image = db.relationship("Image",
                                 foreign_keys = main_image_id)

    _endpoint = "main.post"

    __mapper_args__ = { "polymorphic_identity": "post" }

    def edit_link(self):
        href = url_for("post.edit", slug=self.slug)
        link = "<a class='btn btn-primary' href={}>Edit</a>".format(href)
        return Markup(link)

    def delete_form(self):
        from ..bp_post.forms import DeletePostForm
        form = DeletePostForm(self)
        return form()

    # generate fake
    @classmethod
    def generate_fake(cls, count=100):
        from random import seed, randint
        import forgery_py
        from sqlalchemy.exc import IntegrityError

        seed()
        users = [user
                 for user in User.query.all()
                 if user.can(Permission.WRITE_POST)]
        user_count = len(users)
        for i in range(count):
            u = users[randint(0, user_count-1)]
            p = cls(name = forgery_py.lorem_ipsum.title(),
                    excerpt = forgery_py.lorem_ipsum.paragraph(),
                    body_md = forgery_py.lorem_ipsum.paragraphs(3),
                    status = True,
                    author = u)
            db.session.add(p)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


db.event.listen(Post.name,    "set", Post.on_changed_name)
db.event.listen(Post.body_md, "set", Post.on_changed_body)


class Category(MainContentMixin, NameMixin, MenuItem):
    id = db.Column(db.Integer, db.ForeignKey("menuitem.id"), primary_key=True)
    excerpt = db.Column(db.Text)
    # hierarchy
    parent_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    children = db.relationship("Category",
                               backref = db.backref("parent", remote_side=id),
                               foreign_keys = parent_id)
    # relationship w/ Image
    main_image_id = db.Column(db.Integer, db.ForeignKey("image.id"))
    main_image = db.relationship("Image",
                                 foreign_keys = main_image_id)
    #
    _endpoint = "main.category"

    __mapper_args__ = { "polymorphic_identity": "category" }

    def tree(self, linked=True):
        e = self
        tree_list = [e]
        while e.parent is not None:
            e = self.__class__.query.get(e.parent_id)
            tree_list.insert(0, e)
        if linked:
            output = " > ".join([e.link() for e in tree_list])
        else:
            output = " > ".join([e.name for e in tree_list])
        return Markup(output)


db.event.listen(Category.name, "set", Category.on_changed_name)


class Tag(MainContentMixin, NameMixin, MenuItem):
    id = db.Column(db.Integer, db.ForeignKey("menuitem.id"), primary_key=True)
    # relationship w/ Post
    posts = db.relationship("Post",
                            secondary = post_tag,
                            back_populates = "tags")
    #
    _endpoint = "main.tag"

    __mapper_args__ = { "polymorphic_identity": "tag" }


db.event.listen(Tag.name, "set", Tag.on_changed_name)


class Image(MainContentMixin, BaseModel):
    filename = db.Column(db.String(128), index=True, unique=True, nullable=False)
    alternative = db.Column(db.String(128))
    caption =db.Column(db.Text)
    # relationship w/ Category
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    category = db.relationship("Category",
                               backref = "images",
                               foreign_keys = category_id)
    # relationship w/ Post
    posts = db.relationship("Post",
                            secondary = post_image,
                            back_populates = "images")

    def _get_name(self):
        return self.alternative or self.filename
