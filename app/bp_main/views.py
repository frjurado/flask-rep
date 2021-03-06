# -*- coding: utf-8 -*-
from flask import request, render_template, current_app
from flask.ext.login import current_user
from flask.views import View
from . import main
from ..bp_post.forms import CommentForm, GuestCommentForm
from ..models.users import User
from ..models.content import Post, Category, Tag
from ..helpers import get_or_404


class PostList(View):
    def __init__(self, **kwargs):
        super(PostList, self).__init__(**kwargs)
        self.title = None

    def query(self, **kwargs):
        raise NotImplementedError()

    def render_template(self, context):
        return render_template('post_list.html', **context)

    def dispatch_request(self, **kwargs):
        query = self.query(**kwargs).filter(Post.page.is_(False)).order_by(Post.created.desc())
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['POSTS_PER_PAGE']
        pagination = query.paginate(page, per_page=per_page, error_out=True)
        posts = pagination.items
        context = { 'title': self.title,
                    'pagination': pagination,
                    'posts': posts }
        return self.render_template(context)


class IndexList(PostList):
    def query(self, **kwargs):
        return Post.query


class AuthorList(PostList):
    def query(self, **kwargs):
        author = get_or_404(User, User.username == kwargs['username'])
        self.title = u"Posts by {}".format(author.name or author.username)
        return Post.query.filter_by(author=author)


class TagList(PostList):
    def query(self, **kwargs):
        tag = get_or_404(Tag, Tag.slug == kwargs['slug'])
        self.title = u"Posts tagged {}".format(tag.name)
        return Post.query.filter(Post.tags.contains(tag))


class CategoryList(PostList):
    def query(self, **kwargs):
        category = get_or_404(Category, Category.slug == kwargs['slug'])
        self.title = u"Posts under category {}".format(category.name)
        return Post.query.filter_by(category=category)


main.add_url_rule('/',                  view_func=IndexList.as_view('index'))
main.add_url_rule('/author/<username>', view_func=AuthorList.as_view('author'))
main.add_url_rule('/tag/<slug>',        view_func=TagList.as_view('tag'))
main.add_url_rule('/category/<slug>',   view_func=CategoryList.as_view('category'))


@main.route('/<slug>')
def post(slug):
    post = get_or_404(Post, Post.slug == slug)
    if current_user.is_authenticated:
        form = CommentForm(post)
    else:
        form = GuestCommentForm(post)
    return render_template('post.html', post=post, form=form)
