# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask.ext.login import login_required, current_user
from . import post
from .forms import PostForm, DeletePostForm, ImageForm, DropForm
from .. import db, images
from ..models.users import Permission
from ..models.content import Post, Category, Tag, Image
from ..decorators import permission_required
from ..helpers import get_or_404 # necessary?


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
    drop_form = DropForm()
    if form.validate_on_submit():
        post = Post( name = form.name.data,
                     excerpt = form.excerpt.data,
                     body_md = form.body_md.data,
                     author = current_user._get_current_object() )
        # tags
        set_tags(post, form._tag_list)
        # categories
        set_categories(post, form.old_category.data, form._category_list)
        #
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post', slug=post.slug))
    old_photos = Image.query.all()
    return render_template('write_post.html',
                           form=form,
                           drop_form=drop_form,
                           old_photos=old_photos)


@post.route('/edit/<slug>', methods=["GET", "POST"])
@login_required
def edit(slug):
    post = get_or_404(Post, Post.slug == slug)
    form = PostForm(obj=post)
    drop_form = DropForm()
    if form.validate_on_submit():
        post.name = form.name.data
        post.excerpt = form.excerpt.data
        post.body_md = form.body_md.data
        # tags
        post.tags[:] = []
        set_tags(post, form._tag_list)
        # categories
        set_categories(post, form.old_category.data, form._category_list)
        #
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post', slug=post.slug))
    new_photos = post.images
    old_photos = Image.query.filter(~Image.id.in_([i.id for i in post.images])).all()
    form.tags.data = ", ".join([tag.name for tag in post.tags])
    if post.category is not None:
        form.old_category.data = post.category.id
    return render_template('write_post.html',
                           form=form,
                           drop_form=drop_form,
                           new_photos=new_photos,
                           old_photos=old_photos)


@post.route('/delete/<slug>', methods=["POST"])
@login_required
@permission_required(Permission.EDIT_POST)
def delete(slug):
    form = DeletePostForm()
    if form.validate_on_submit():
        db.session.delete(form.post)
        flash(u"Post was deleted.")
        return redirect(url_for('main.index'))
    flash(u"Somethong bad happened.")
    return redirect(url_for('main.index')) # referrer?


@post.route('/file/_upload', methods=["POST"])
def _upload():
    form = DropForm()
    if form.validate_on_submit():
        filename = images.save(request.files['file'])
        i = Image(
            filename=filename,
            alternative = form.alternative.data,
            caption = form.caption.data,
        )
        db.session.add(i)
        return jsonify(filename=i.filename, tag=i.img())
