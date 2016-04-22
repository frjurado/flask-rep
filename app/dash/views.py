from flask import request, render_template, redirect, url_for, flash, abort, current_app
from flask.ext.login import current_user, login_required, fresh_login_required
from . import dash
from .. import db
from .forms import *
from ..models import User, Role, Permission
from ..decorators import *


@dash.route('/')
@member_required
def dashboard():
    return redirect(url_for('dash.user_profile', username=current_user.username))


# helper for user list and profiles
def user_forms(user):
    if user.get_role() == "Blocked":
        user.unblock_form = UnblockUserForm(user=user)
        user.delete_form = DeleteAccountForm(user=user)
    elif user.get_role() == "Guest":
        user.block_form = BlockUserForm(user=user)
    elif not user.is_main_administrator() and user != current_user:
        user.assign_form = AssignRoleForm(user=user)
        user.banish_form = BanishUserForm(user=user)

@dash.route('/users')
@admin_required
def user_list():
    users = User.query.all()
    for user in users:
        user_forms(user)
    return render_template('user_list.html', users=users)

@dash.route('/user/<username>')
@admin_or_self_required
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    if current_user.is_administrator():
        user_forms(user)
    return render_template('user_profile.html', user=user)

@dash.route('/user/<username>/edit', methods=["GET", "POST"])
@admin_or_self_required
def edit_user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    form = EditUserProfileForm()
    if form.validate_on_submit():
        user.name = form.name.data
        user.url = form.url.data
        user.newsletter = form.newsletter.data
        db.session.add(user)
        flash("Changes were saved.")
        return redirect(url_for('dash.user_profile', username = user.username))
    form.name.data = user.name or ""
    form.url.data = user.url or ""
    form.newsletter.data = user.newsletter
    return render_template('edit_user_profile.html', user=user, form=form)


# asign roles, block, unblock, banish, delete
@dash.route('/user/assign-role', methods=['POST'])
@admin_required
def assign_role():
    form = AssignRoleForm(formdata=request.form)
    if form.validate_on_submit():
        user = form.user
        if user.set_role(form.role):
            flash("Role for {0} updated to {1}".format(user.username, user.role.name))
            db.session.add(user)
    return redirect(url_for('dash.user_list'))

@dash.route('/user/banish', methods=['POST'])
@admin_required
def banish_user():
    form = BanishUserForm(formdata=request.form)
    if form.validate_on_submit():
        user = form.user
        if user.banish():
            flash("User {0} was set as guest".format(user.username))
            db.session.add(user)
    return redirect(url_for('dash.user_list'))

@dash.route('/user/block', methods=['POST'])
@admin_required
def block_user():
    form = BlockUserForm(formdata=request.form)
    if form.validate_on_submit():
        user = form.user
        if user.block():
            flash("User {0} was blocked".format(user.username))
            db.session.add(user)
    return redirect(url_for('dash.user_list'))

@dash.route('/user/unblock', methods=['POST'])
@admin_required
def unblock_user():
    form = UnblockUserForm(formdata=request.form)
    if form.validate_on_submit():
        user = form.user
        if user.unblock():
            flash("User {0} was unblocked".format(user.username))
            db.session.add(user)
    return redirect(url_for('dash.user_list'))

@dash.route('/user/delete-account', methods=['POST'])
@admin_or_self_required
def delete_account():
    form = DeleteAccountForm(formdata=request.form)
    if form.validate_on_submit():
        user = form.user
        flash("User {0} was deleted".format(user.username))
        db.session.delete(user)
    return redirect(url_for('dash.user_list'))
