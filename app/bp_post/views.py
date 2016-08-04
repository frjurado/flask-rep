from flask import render_template, redirect, url_for, flash
from flask.ext.login import login_required, current_user
from . import post
from .forms import PostForm, DeletePostForm
from .. import db
from ..models.users import Permission
from ..models.content import Post, Category, Tag
from ..decorators import permission_required
from ..helpers import get_or_404


# helpers
def set_tags(post, tags):
    for name in tags:
        tag = Tag.query.filter_by(name=name).first()
        if tag is None:
            tag = Tag(name=name)
            db.session.add(tag)
        post.tags.append(tag)


def set_categories(post, old, new):
    """
    Just now, old should be the id of an existing category;
              new should be a list of new category names.
    """
    c = None
    if new:
        c = Category(name=new.pop())
        parent = c
        son = None
        while new:
            son = parent
            parent = Category(name=new.pop())
            son.parent = parent
            db.session.add(parent)
        if old:
            old_c = Category.query.get(old)
            parent.parent = old_c
    elif old:
        c = Category.query.get(old)
    if c is not None:
        db.session.add(c)
        post.category = c


# views
@post.route('/write', methods=["GET", "POST"])
@login_required
@permission_required(Permission.WRITE_POST)
def write():
    form = PostForm()
    if form.validate_on_submit():
        post = Post( name = form.name.data,
                     excerpt = form.excerpt.data,
                     body_md = form.body_md.data,
                     author = current_user._get_current_object() ) # destroy current_user!
        # tags
        set_tags(post, form._tag_list)
        # categories
        set_categories(post, form.old_category.data, form._category_list)
        #
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post', slug=post.slug))
    return render_template('write_post.html', form=form)


@post.route('/edit/<slug>', methods=["GET", "POST"])
@login_required
def edit(slug):
    post = get_or_404(Post, Post.slug == slug)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.name = form.name.data
        post.excerpt = form.excerpt.data
        post.body_md = form.body_md.data
        # tags
        post.tags[:] = []
        set_tags(post, form._tag_list)
        # categories
        set_categories(post, form.old_category.data, form._category_list)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post', slug=post.slug))
    form.tags.data = ", ".join([tag.name for tag in post.tags])
    form.old_category.data = post.category.id
    return render_template('write_post.html', form=form)


@post.route('/delete/<slug>', methods=["POST"])
@login_required
@permission_required(Permission.EDIT_POST)
def delete(slug):
    form = DeletePostForm()
    if form.validate_on_submit():
        db.session.delete(form.post)
        flash("Post was deleted.")
        return redirect(url_for('main.index'))
    flash("Somethong bad happened.")
    return redirect(url_for('main.index')) # referrer?


# ####
# # import os
# from flask import current_app, request, send_from_directory
# # from werkzeug.utils import secure_filename
# from .forms import ImageForm
# from .. import images
# from .._models import Attachment
# #
# # def allowed_file(filename):
# #     return "." in filename \
# #         and filename.rsplit(".", 1)[1] in current_app.config['ALLOWED_EXTENSIONS']
# #
# #
# @post.route('/file/upload', methods=['GET', 'POST'])
# def file_upload():
#     print
#     print "within file_upload..."
#     form = ImageForm()
#     if form.validate_on_submit():
#         filename = images.save(request.files['image'])
#         print "filename = {}".format(filename)
#         a = Attachment(
#             name=filename,
#             excerpt=form.caption.data,
#             author=current_user._get_current_object()
#         )
#         db.session.add(a)
#         print "database object = {}".format(a)
#         flash("Photo was saved!")
#         return redirect(url_for('post.file_view', filename=filename))
#     return render_template('file_upload.html', form=form)
# #         f = request.files['image']
# #         if f and allowed_file(f.filename):
# #             filename = secure_filename(f.filename)
# #             f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
# #             return redirect(url_for('post.file_view', filename=filename))
# #     return render_template('file_upload.html', form=form)
# #
# @post.route('/file/<filename>')
# def file_view(filename):
#     print
#     print "within file_view..."
#     photo = get_or_404(Attachment, Attachment.name == filename)
#     print "database object = {}".format(photo)
#     url = images.url(photo.name)
#     print "filename = {}".format(photo.name)
#     print "url = {}".format(url)
#     # print ">>>"
#     # print current_app.config["UPLOADS_DEFAULT_DEST"]
#     # return send_from_directory(current_app.config["UPLOADS_DEFAULT_DEST"],
#     #                           photo.name)
#     # return url
#     return render_template("photo.html", url=url, photo=photo)
