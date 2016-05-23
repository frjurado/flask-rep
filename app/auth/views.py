from flask import request, render_template, redirect, url_for, flash
from flask.ext.login import current_user, login_user, logout_user, \
        login_required, fresh_login_required
import email
from . import auth
from .forms import *
from .. import db
from ..models import User
from ..decorators import signup_enabled, anonymous_required, main_admin_excluded
from ..helpers import invalid_token, next_or_index, to_dashboard


def auth_form(form, login=False, signup=False):
    return render_template('auth_form.html',
                           form = form,
                           login = login,
                           signup = signup)


# main auth views
@auth.route('/signup', methods=['GET', 'POST'])
@signup_enabled
@anonymous_required
def signup():
    """
    Signup view.
    If GET or ValidationError, render 'auth/signup.html'.
    If valid POST, add to database and send confirmation email.
    """
    form = SignupForm()
    if form.validate_on_submit():
        user = User( email    = form.email.data,
                     username = form.username.data,
                     password = form.password.data )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        email.confirm(user, token)
        flash("A confirmation link has been sent to you. Please check email.")
        login_user(user)
        return to_dashboard()
    return auth_form(form, signup=True)


@auth.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    """
    Login view.
    If GET or ValidationError, render 'auth/login.html'.
    If valid POST, login user.
    """
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user, form.remember_me.data)
        flash("Welcome back!")
        return to_dashboard()
    return auth_form(form, login=True)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("See you soon!")
    return next_or_index()


# confirmation
@auth.route('/confirm')
@login_required
def resend_confirmation():
    """
    Get a new confirmation token (if expired or if mail was lost).
    """
    if current_user.confirmed:
        flash("Your account is already confirmed.")
        return next_or_index()
    token = current_user.generate_confirmation_token()
    email.confirm(current_user, token)
    flash("A new confirmation link has been sent to you. Please check email.")
    return to_dashboard()


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """
    args: token.
    Check given token and set user.confirm to True.
    """
    if current_user.confirmed:
        return next_or_index()
    if not current_user.confirm(token):
        invalid_token()
    flash("You have confirmed your account. Welcome!")
    return to_dashboard()


# data changes
@auth.route('/change-email', methods=['GET', 'POST'])
@fresh_login_required
@main_admin_excluded
def change_email_request():
    """
    Change email associated with your account.
    The new email will be pending until you confirm it.
    """
    form = ChangeEmailForm(current_user)
    if form.validate_on_submit():
        new_email = form.email.data
        token = current_user.generate_email_change_token(new_email)
        email.change_email(current_user, new_email, token)
        flash("A confirmation link has been sent to your new email.")
        return to_dashboard()
    return auth_form(form)


@auth.route('/change-email/<token>')
@fresh_login_required
@main_admin_excluded
def change_email(token):
    """
    args: token.
    Check token and actually refresh your email.
    """
    if not current_user.change_email(token):
        invalid_token()
    flash("Your new email has been confirmed.")
    return to_dashboard()


@auth.route('/change-username', methods=['GET', 'POST'])
@fresh_login_required
def change_username():
    form = ChangeUsernameForm(current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.add(current_user)
        flash("You changed your username.")
        return to_dashboard()
    return auth_form(form)


@auth.route('/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    form = ChangePasswordForm(current_user)
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.add(current_user)
        flash("You changed your password.")
        return to_dashboard()
    return auth_form(form)


# username & password reset
@auth.route('/reset', methods=['GET', 'POST'])
@anonymous_required
def reset_request():
    """
    For forgotten login credentials, request to change them.
    """
    form = ResetRequestForm()
    if form.validate_on_submit():
        token = form.user.generate_reset_token()
        email.reset(form.user, token)
        flash("An email with instructions has been sent to you.")
        return next_or_index()
    return auth_form(form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
@anonymous_required
def reset(token):
    """
    args: token.
    Check token and allow to reset your username and password.
    """
    form = ResetForm(token)
    if form.validate_on_submit():
        form.user.reset(form.username.data, form.password.data)
        login_user(form.user)
        flash("Your username and password have been updated.")
        return to_dashboard()
    return auth_form(form)
