from flask import \
    request, session, render_template, redirect, url_for, flash, current_app, abort
from flask.ext.login import login_required
from . import main
from .. import db
from ..models import User, Role, Post
from ..email import send_email


@main.route('/', methods=['GET', 'POST'])
def index():
    """
    Simple index view.
    """
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.created.desc()).paginate(
        page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=True
    )
    posts = pagination.items
    return render_template('index.html', pagination=pagination, posts=posts)


@main.route('/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first()
    if post is None:
        abort(404)
    return render_template('post.html', post=post)
