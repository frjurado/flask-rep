from flask import request, render_template, current_app, abort
from flask.views import View
from . import main
from ..models import User, Post


class PostList(View):
    title = None

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
        author = User.query.filter_by(username=kwargs['username']).first()
        if author is None:
            abort(404)
        self.title = "Posts by {}".format(author.name or author.username)
        return Post.query.filter_by(author=author)


main.add_url_rule('/',
                  view_func=IndexList.as_view('index'))
main.add_url_rule('/author/<username>',
                  view_func=AuthorList.as_view('author'))

@main.route('/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first()
    if post is None:
        abort(404)
    return render_template('post.html', post=post)
