# -*- coding: utf-8 -*-
import re
from wtforms import StringField, TextAreaField, HiddenField, SelectField, FileField
from wtforms.validators import Required, Regexp, InputRequired, ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..forms import BaseForm, InlineForm, ModalForm
from ..models.content import Post, Category


class PostForm(BaseForm):
    _submit = u"Submit post"

    name = StringField(u"Title", validators=[InputRequired()])
    excerpt = TextAreaField(u"Excerpt", validators=[InputRequired()])
    old_category = SelectField(u"Old category", coerce=int) # use a form field!
    new_category = StringField(u"New category")
    _category_list = None
    tags = StringField(u"Tags")
    _tag_list = None
    body_md = PageDownField(u"Body", validators=[InputRequired()])

    def __init__(self, **kwargs):
        super(PostForm, self).__init__(**kwargs)
        self.old_category.choices = [(0, u"No category")]
        stack = Category.query.filter_by(parent_id=None)\
                              .order_by(Category.name.desc())\
                              .all()
        while stack:
            e = stack.pop()
            if e.children:
                stack.extend(e.children)
            self.old_category.choices.append( (e.id, e.tree(linked=False)) )

    def validate_new_category(self, field):
        field.data = field.data.strip()
        if field.data:
            self._category_list = [e.strip() for e in field.data.split(">")]
            for name in self._category_list:
                if Category.query.filter_by(name=name).first() is not None:
                    raise ValidationError(u"Don't recreate an existing category.")

    def validate_tags(self, field):
        if field.data is not None:
            self._tag_list = [e.strip() for e in field.data.split(',') if e.strip()]


class DeletePostForm(InlineForm):
    _danger = True

    _endpoint = 'post.delete'
    _submit = u"Delete"

    slug = HiddenField(validators=[InputRequired()])

    def __init__(self, post=None, **kwargs):
        super(DeletePostForm, self).__init__(**kwargs)
        if post is not None:
            self.slug.data = post.slug
            self._endpoint_kwargs = {'slug': self.slug.data}

    def validate_slug(self, field):
        post = Post.query.filter_by(slug=field.data).first()
        if post is None:
            raise ValidationError("Invalid post.")
        self.post = post


####
class ImageForm(BaseForm): # deprecated
    _enctype = "multipart/form-data"
    image = FileField(u"Image file", validators = [Required()])
    #,Regexp("""^[^\s]+\.(jpe?g|png)$""")
    alternative = StringField(u"Alternative text")
    caption = TextAreaField(u"Caption")

    # def validate_image(form, field):
    #     field.data = re.sub(r'[^a-z0-9_-]', '_', field.data)

class DropForm(ModalForm):
    _submit = u"Upload"
    _title = u"Upload a photo"
    _endpoint = 'post._upload'
    _enctype = "multipart/form-data"
    _form_classes = ['dropzone']

    alternative = StringField(u"Alternative text")
    caption = TextAreaField(u"Caption")
