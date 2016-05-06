from flask import current_app, request, render_template, redirect, url_for, flash, abort
from flask.ext.login import current_user, login_user, logout_user, \
        login_required, fresh_login_required
from . import auth
from .. import db
import email
from .forms import *
from ..models import User
from ..decorators import signup_enabled, anonymous_required, main_admin_excluded


# helper functions (somewhere else?)
# ---------------------------------------------------------
def next_or_index():
    return redirect(request.args.get('next') or url_for('main.index'))


# before request
# ---------------------------------------------------------
@auth.before_app_request
def before_request():
    """
    Refresh last_seen attribute if authenticated.
    """
    # if current_user.is_authenticated:
    #     current_user.ping()


# main auth views
# ---------------------------------------------------------
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
        return redirect(url_for('dash.dashboard'))
    return render_template('signup.html', form=form)

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
        return redirect(url_for('dash.dashboard'))
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("See you soon!")
    return next_or_index()


# confirmation
# ---------------------------------------------------------
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
    return next_or_index()

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """
    args: token.
    Check given token and set user.confirm to True.
    """
    if current_user.confirmed:
        return next_or_index()
    if current_user.confirm(token):
        flash("You have confirmed your account. Welcome!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return next_or_index()


# email change
# ---------------------------------------------------------
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
        return next_or_index()
    return render_template('simple_form.html', form=form)

@auth.route('/change-email/<token>')
@fresh_login_required
@main_admin_excluded
def change_email(token):
    """
    args: token.
    Check token and actually refreshing your email.
    """
    if current_user.change_email(token):
        flash("Your new email has been confirmed.")
    else:
        flash("Invalid or expired token.")
    return next_or_index()


# username change
# ---------------------------------------------------------
@auth.route('/change-username', methods=['GET', 'POST'])
@fresh_login_required
def change_username():
    """
    Change your username.
    """
    form = ChangeUsernameForm(current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.add(current_user)
        flash("You changed your username.")
        return next_or_index()
    return render_template('simple_form.html', form=form)


# password change
# ---------------------------------------------------------
@auth.route('/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    """
    Change your password.
    """
    form = ChangePasswordForm(current_user)
    if form.validate_on_submit():
        current_user.password = form.password_new.data
        db.session.add(current_user)
        flash("You changed your password.")
        return next_or_index()
    return render_template('simple_form.html', form=form)


# username & password reset
# ---------------------------------------------------------
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
    return render_template('simple_form.html', form=form)

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
        return next_or_index()
    return render_template('simple_form.html', form=form)
