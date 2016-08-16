# -*- coding: utf-8 -*-
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Regexp, Email, EqualTo
from wtforms.validators import ValidationError
from ..forms import BaseForm
from ..models.users import User
from ..helpers import serialize, load_token, invalid_token


# validators ------------------------------------------------------------------
def verify_email(form, field):
    user = User.query.filter_by(email=field.data).first()
    if user is None:
        raise ValidationError(u"Unknown email address.")
    form.user = user


def verify_password(form, field):
    if form.user is not None:
        if not form.user.verify_password(field.data):
            raise ValidationError(u"Invalid password")
    else:
        user = User.query.filter_by(username=form.username_old.data).first()
        if user is None or not user.verify_password(field.data):
            raise ValidationError(u"Invalid username or password")
        form.user = user


def verify_available(form, field):
    user = User.query.filter(getattr(User, field.id) == field.data).first()
    if form.user is not None and field.data == getattr(form.user, field.id):
        if not isinstance(form, ResetForm):
            raise ValidationError(u"That's already your {}.".format(field.id))
    elif user:
        raise ValidationError(u"{} already in use.".format(field.id.capitalize()))


# fields ----------------------------------------------------------------------
class EmailOldField(StringField):
    def __init__(self, label=u"Email", **kwargs):
        super(EmailOldField, self).__init__(
            label = label,
            validators = [InputRequired(), Email(), verify_email],
            **kwargs)


class EmailNewField(StringField):
    def __init__(self, label=u"Email", **kwargs):
        super(EmailNewField, self).__init__(
            label = label,
            validators = [InputRequired(), Email(), verify_available],
            **kwargs)


class UsernameOldField(StringField):
    def __init__(self, label=u"Username", **kwargs):
        super(UsernameOldField, self).__init__(
            label = label,
            validators = [InputRequired()],
            **kwargs)


class UsernameNewField(StringField):
    def __init__(self, label=u"Username", **kwargs):
        regexp = """[A-Za-z0-9_.]{3,64}"""
        message = u"""
        Username must be between 3 and 64 characters,
        and must only contain letters, numbers, dots and underscores.
        """
        validators=[InputRequired(), Regexp(regexp,0,message), verify_available]
        super(UsernameNewField, self).__init__(
            label = label,
            validators = validators,
            **kwargs)


class PasswordOldField(PasswordField):
    def __init__(self, label=u"Password", **kwargs):
        super(PasswordOldField, self).__init__(
            label = label,
            validators = [InputRequired(), verify_password],
            **kwargs)


class PasswordNewField(PasswordField):
    def __init__(self, label=u"Password", **kwargs):
        regexp = """^(?=.*[a-zA-Z])(?=.*\d)(?=.*[-!$%^&*()_+|~=`{}\[\]:";'<>?,.\/]).{8,64}$"""
        message = u"""
        Password must be between 8 and 64 characters,
        and must contain at least one letter, digit and symbol.
        """
        validators = [InputRequired(), Regexp(regexp,0,message)]
        super(PasswordNewField, self).__init__(
            label = label,
            validators = validators,
            **kwargs)


class PasswordConfirmField(PasswordField):
    def __init__(self, label="uConfirm password", **kwargs):
        validators = [InputRequired(), EqualTo("password", u"Passwords don't match.")]
        super(PasswordConfirmField, self).__init__(
            label = label,
            validators = validators,
            **kwargs)


# forms -----------------------------------------------------------------------
class UserForm(BaseForm):
    def __init__(self, **kwargs):
        super(UserForm, self).__init__(**kwargs)
        self.user = None


class ChangeUserForm(BaseForm):
    _submit = u"Change"
    def __init__(self, user, **kwargs):
        super(ChangeUserForm, self).__init__(**kwargs)
        self.user = user


class SignupForm(UserForm):
    _title = u"Sign up"
    email = EmailNewField()
    username = UsernameNewField()
    password = PasswordNewField()
    password_confirm = PasswordConfirmField()


class LoginForm(UserForm):
    _title = u"Log in"
    username_old = UsernameOldField()
    password_old = PasswordOldField()
    remember_me = BooleanField(u"Keep me logged in")


class ChangeEmailForm(ChangeUserForm):
    _title = u"Change email"
    email = EmailNewField(u"New email")
    password_old = PasswordOldField()


class ChangeUsernameForm(ChangeUserForm):
    title = u"Change username"
    username = UsernameNewField(u"New username")
    password_old = PasswordOldField()


class ChangePasswordForm(ChangeUserForm):
    _title = u"Change password"
    password_old = PasswordOldField(u"Old password")
    password = PasswordNewField(u"New password")
    password_confirm = PasswordConfirmField(u"Confirm new password")


class ResetRequestForm(UserForm):
    _submit = u"Reset"
    _title = u"Request account reset"
    email_old = EmailOldField()


class ResetForm(UserForm):
    _submit = u"Reset"
    _title = u"Reset username and password"
    username = UsernameNewField(u"New username")
    password = PasswordNewField(u"New password")
    password_confirm = PasswordConfirmField()

    def __init__(self, token, **kwargs):
        super(ResetForm, self).__init__(**kwargs)
        s = serialize()
        data = load_token(s, token)
        if data is None:
            invalid_token()
        self.user = User.query.get(data.get('reset'))
        if self.user is None:
            invalid_token()
