# -*- coding: utf-8 -*-
import re
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, FormField, HiddenField, SelectField, FileField
from wtforms.validators import Regexp, InputRequired, ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..forms import BaseForm, InlineForm, ModalForm
from ..models.content import Post, Category, Image, Comment


class CategoryFields(Form):
    _list = None

    old = SelectField(u"Old category", coerce=int)
    new = StringField(u"New category")

    def validate_new(self, field):
        data = field.data.strip()
        if data:
            self._list = [e.strip() for e in data.split(">")]
            for name in self._list:
                if Category.query.filter_by(name=name).first() is not None:
                    raise ValidationError(u"Don't recreate an existing category.")

class PostForm(BaseForm):
    _submit = u"Submit post"
    _tag_list = None
    _main_image = None

    page = BooleanField(u"Page")
    name = StringField(u"Title", validators=[InputRequired()])
    excerpt = TextAreaField(u"Excerpt")
    categories = FormField(CategoryFields)
    tags = StringField(u"Tags")
    main_image_id = StringField(u"Main image")
    body_md = PageDownField(u"Body", validators=[InputRequired()])

    def __init__(self, **kwargs):
        super(PostForm, self).__init__(**kwargs)
        self.categories.old.choices = [(0, u"No category")]
        stack = Category.query.filter_by(parent_id=None)\
                              .order_by(Category.name.desc())\
                              .all()
        while stack:
            e = stack.pop()
            if e.children:
                stack.extend(e.children)
            self.categories.old.choices.append( (e.id, e.tree(linked=False)) )

    def validate_tags(self, field):
        if field.data is not None:
            self._tag_list = [e.strip() for e in field.data.split(',') if e.strip()]

    def validate_main_image_id(self, field):
        filename = field.data.strip()
        if filename:
            image = Image.query.filter_by(filename=filename).first()
            if image is None:
                raise ValidationError(u"Invalid main image.")
            self._main_image = image


class DeletePostForm(InlineForm):
    _danger = True

    _endpoint = 'post.delete'
    _submit = u"Del"

    slug = HiddenField(validators=[InputRequired()])

    def __init__(self, post=None, **kwargs):
        super(DeletePostForm, self).__init__(**kwargs)
        if post is not None:
            self.slug.data = post.slug
            self._endpoint_kwargs = {'slug': self.slug.data}

    def validate_slug(self, field):
        post = Post.query.filter_by(slug=field.data).first()
        if post is None:
            raise ValidationError(u"Invalid post.")
        self.post = post


class StatusForm(InlineForm):
    _endpoint = 'post._status'
    _submit = u"On/Off"
    _form_classes = ["status-form"]

    slug = HiddenField(validators=[InputRequired()])

    def __init__(self, post=None, **kwargs):
        super(StatusForm, self).__init__(**kwargs)
        self.post = None
        if post is not None:
            self.post = post #not necessary?
            self.slug.data = post.slug
            self._endpoint_kwargs = {'slug': self.slug.data}

    def _id(self):
        name = self.__class__.__name__
        if self.post is not None:
            return name[0].lower() + name[1:] + str(self.post.id)
        else:
            return name[0].lower() + name[1:]

    def validate_slug(self, field):
        post = Post.query.filter_by(slug=field.data).first()
        if post is None:
            raise ValidationError(u"Invalid post.")
        self.post = post


class DropForm(ModalForm):
    _submit = u"Upload"
    _title = u"Upload a photo"
    _endpoint = 'post._upload'
    _enctype = "multipart/form-data"
    _form_classes = ['dropzone']

    alternative = StringField(u"Alternative text")
    caption = TextAreaField(u"Caption")


class CommentForm(BaseForm):
    _submit = u"Comment"
    _title = u"Leave a comment"
    _endpoint = 'post._comment'
    _form_classes = ["commentForm"]

    post_slug = HiddenField(validators=[InputRequired()])
    parent_id = HiddenField()
    body_md = TextAreaField("", validators=[InputRequired()])

    def __init__(self, post=None, **kwargs):
        super(CommentForm, self).__init__(**kwargs)
        if post is not None:
            self.post_slug.data = post.slug
            self._endpoint_kwargs = {'slug': self.post_slug.data}

    def validate_post_slug(self, field):
        post = Post.query.filter_by(slug=field.data).first()
        if post is None:
            raise ValidationError(u"Invalid post.")
        self.post = post

    def validate_parent_id(self, field):
        parent = Comment.query.get(str(field.data))
        self.parent = parent or None


class GuestCommentForm(CommentForm):
    author_email = StringField(u"Email", validators=[InputRequired()])
    author_name = StringField(u"Name", validators=[InputRequired()])
    author_url = StringField(u"URL")
