from flask import render_template, flash, redirect, url_for, request, abort
from flask.ext.login import current_user, login_required
from . import user
from .forms import NameForm, UrlForm, DeleteForm, RoleForm
from .. import db
from ..models.users import User
from ..decorators import admin_required, self_required, admin_or_self_required
from ..helpers import get_or_404


@user.route('/')
@login_required
@admin_required
def list():
    users = User.query.all()
    for user in users:
        if user != current_user:
            user.role_form = RoleForm(user)
        if user.get_role() == "Guest":
            user.delete_form = DeleteForm(user)
    return render_template('user_list.html', users=users)


@user.route('/<username>')
@login_required
@admin_or_self_required
def profile(username):
    user = get_or_404(User, User.username == username)
    forms = {}
    you = user == current_user
    admin = current_user.is_administrator()
    if you:
        forms['name'] = NameForm(user)
        forms['url'] = UrlForm(user)
    if admin and not you:
        forms['role'] = RoleForm(user)
        if user.get_role() == "Guest":
            forms['delete'] = DeleteForm(user)
    return render_template('profile.html',
                           user=user, forms=forms, you=you, admin=admin)


@user.route('/edit/<username>', methods=["POST"])
@login_required
@self_required
def edit_profile(username):
    if 'name' in request.form:   # from here...
        form = NameForm()        #
    elif 'url' in request.form:  #
        form = UrlForm()         #
    else:                        #
        flash("Invalid request.")#
        abort(404)               # ...to here: ugly! (within the form class?)
    if form.validate_on_submit():
        user = form.user
        form.populate_obj(user)
        db.session.add(user)
        return redirect(url_for('user.profile', username=username))
    flash("Invalid form thing") # ugly...
    return redirect(url_for('user.profile', username=username))


@user.route('/role/<username>', methods=["POST"])
@login_required
@admin_required
def assign_role(username):
    form = RoleForm()
    if form.validate_on_submit():
        # population is done within the form itself!
        return redirect(url_for('user.profile', username=username)) # but if list...
    flash("Invalid form thing") # ugly...
    return redirect(url_for('user.profile', username=username))


@user.route('/delete/<username>', methods=["POST"])
@login_required
@admin_required
def delete_account(username):
    form = DeleteForm()
    if form.validate_on_submit():
        # should check it's a guest!
        db.session.delete(form.user)
        flash("The user account was deleted.")
        return redirect(url_for('user.list'))
    flash("Something bad happened.")
    return redirect(url_for('user.list'))
