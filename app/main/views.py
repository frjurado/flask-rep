from flask import request, render_template, current_app, abort
from flask.views import View
from . import main
from ..models import User, Post
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
        query = self.query(**kwargs).order_by(Post.created.desc())
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(
            page,
            per_page=current_app.config['POSTS_PER_PAGE'],
            error_out=True
        )
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
        self.title = "Posts by {}".format(author.name or author.username)
        return Post.query.filter_by(author=author)


main.add_url_rule('/',
                  view_func=IndexList.as_view('index'))
main.add_url_rule('/author/<username>',
                  view_func=AuthorList.as_view('author'))

@main.route('/<slug>')
def post(slug):
    post = get_or_404(Post, Post.slug == slug)
    return render_template('post.html', post=post)
