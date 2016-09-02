from flask import render_template, Markup
from .models.content import Category, Tag


class Aside(object):
    template = None
    title = None

    def __init__(self, title=None):
        self.context = { 'title': title or self.title }

    def render_template(self):
        if self.template is None:
            raise NotImplementedError()
        return Markup(render_template('aside/{}'.format(self.template),
                                      **self.context))

    def __call__(self):
        return self.render_template()


class OneStep(Aside):
    template = 'one_step.html'


class CategoryList(Aside):
    template = 'category_list.html'

    def __call__(self, parent=None):
        parent = Category.query.filter_by(name=parent).first()
        categories = Category.query.filter_by(parent=parent).order_by(Category.name).all()
        self.context['title'] = parent.name
        self.context['categories'] = categories
        return super(CategoryList, self).__call__()


class TagCloud(Aside):
    template = 'tag_cloud.html'
    title = u"Etiquetas"

    def __call__(self):
        tags = Tag.query.order_by(Tag.name).all()
        self.context['tags'] = tags
        return super(TagCloud, self).__call__()


one_step = OneStep()
category_list = CategoryList()
tag_cloud = TagCloud()
