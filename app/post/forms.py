from wtforms import StringField, TextAreaField, HiddenField, SelectField
from wtforms.validators import InputRequired, ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..forms import BaseForm
from ..models import Post, Category


class PostForm(BaseForm):
    _submit = "Submit post"

    name = StringField("Title", validators=[InputRequired()])
    excerpt = TextAreaField("Excerpt", validators=[InputRequired()])
    old_category = SelectField("Old category", coerce=int) # use a form field!
    new_category = StringField("New category")
    _category_list = None
    tags = StringField("Tags")
    _tag_list = None
    body_md = PageDownField("Body", validators=[InputRequired()])

    def __init__(self, **kwargs):
        super(PostForm, self).__init__(**kwargs)
        self.old_category.choices = [(0, "No category")]
        stack = Category.query.filter_by(parent_id=None)\
                              .order_by(Category.name.desc())\
                              .all()
        while stack:
            e = stack.pop()
            if e.children:
                stack.extend(e.children)
            self.old_category.choices.append( (e.id, e.tree()) )

    def validate_new_category(self, field):
        field.data = field.data.strip()
        if field.data:
            self._category_list = [e.strip() for e in field.data.split(">")]
            for name in self._category_list:
                if Category.query.filter_by(name=name).first() is not None:
                    raise ValidationError("Don't recreate an existing category.")

    def validate_tags(self, field):
        if field.data is not None:
            self._tag_list = [e.strip() for e in field.data.split(',') if e.strip()]


class DeletePostForm(BaseForm):
    _vertical = False
    _labelled = False
    _danger = True

    _endpoint = 'post.delete'
    _submit = "Delete"

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
