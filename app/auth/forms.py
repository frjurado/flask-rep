from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Regexp, Email, EqualTo
from wtforms.validators import ValidationError
from ..forms import BaseForm
from ..models import User
from ..helpers import serialize, load_token, invalid_token


# validators ------------------------------------------------------------------
def verify_email(form, field):
    user = User.query.filter_by(email=field.data).first()
    if user is None:
        raise ValidationError("Unknown email address.")
    form.user = user


def verify_password(form, field):
    if form.user is not None:
        if not form.user.verify_password(field.data):
            raise ValidationError("Invalid password")
    else:
        user = User.query.filter_by(username=form.username_old.data).first()
        if user is None or not user.verify_password(field.data):
            raise ValidationError("Invalid username or password")
        form.user = user


def verify_available(form, field):
    user = User.query.filter(getattr(User, field.id) == field.data).first()
    if form.user is not None and field.data == getattr(form.user, field.id):
        if not isinstance(form, ResetForm):
            raise ValidationError("That's already your {}.".format(field.id))
    elif user:
        raise ValidationError("{} already in use.".format(field.id.capitalize()))


# fields ----------------------------------------------------------------------
class EmailOldField(StringField):
    def __init__(self, label="Email", **kwargs):
        super(EmailOldField, self).__init__(
            label = label,
            validators = [InputRequired(), Email(), verify_email],
            **kwargs)


class EmailNewField(StringField):
    def __init__(self, label="Email", **kwargs):
        super(EmailNewField, self).__init__(
            label = label,
            validators = [InputRequired(), Email(), verify_available],
            **kwargs)


class UsernameOldField(StringField):
    def __init__(self, label="Username", **kwargs):
        super(UsernameOldField, self).__init__(
            label = label,
            validators = [InputRequired()],
            **kwargs)


class UsernameNewField(StringField):
    def __init__(self, label="Username", **kwargs):
        regexp = """[A-Za-z0-9_.]{3,64}"""
        message = """
        Username must be between 3 and 64 characters,
        and must only contain letters, numbers, dots and underscores.
        """
        validators=[InputRequired(), Regexp(regexp,0,message), verify_available]
        super(UsernameNewField, self).__init__(
            label = label,
            validators = validators,
            **kwargs)


class PasswordOldField(PasswordField):
    def __init__(self, label="Password", **kwargs):
        super(PasswordOldField, self).__init__(
            label = label,
            validators = [InputRequired(), verify_password],
            **kwargs)


class PasswordNewField(PasswordField):
    def __init__(self, label="Password", **kwargs):
        regexp = """^(?=.*[a-zA-Z])(?=.*\d)(?=.*[-!$%^&*()_+|~=`{}\[\]:";'<>?,.\/]).{8,64}$"""
        message = """
        Password must be between 8 and 64 characters,
        and must contain at least one letter, digit and symbol.
        """
        validators = [InputRequired(), Regexp(regexp,0,message)]
        super(PasswordNewField, self).__init__(
            label = label,
            validators = validators,
            **kwargs)


class PasswordConfirmField(PasswordField):
    def __init__(self, label="Confirm password", **kwargs):
        validators = [InputRequired(), EqualTo("password", "Passwords don't match.")]
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
    _submit = "Change"
    def __init__(self, user, **kwargs):
        super(ChangeUserForm, self).__init__(**kwargs)
        self.user = user


class SignupForm(UserForm):
    title = "Sign up"
    email = EmailNewField()
    username = UsernameNewField()
    password = PasswordNewField()
    password_confirm = PasswordConfirmField()


class LoginForm(UserForm):
    title = "Log in"
    username_old = UsernameOldField()
    password_old = PasswordOldField()
    remember_me = BooleanField("Keep me logged in")


class ChangeEmailForm(ChangeUserForm):
    title = "Change email"
    email = EmailNewField("New email")
    password_old = PasswordOldField()


class ChangeUsernameForm(ChangeUserForm):
    title = "Change username"
    username = UsernameNewField("New username")
    password_old = PasswordOldField()


class ChangePasswordForm(ChangeUserForm):
    title = "Change password"
    password_old = PasswordOldField("Old password")
    password = PasswordNewField("New password")
    password_confirm = PasswordConfirmField("Confirm new password")


class ResetRequestForm(UserForm):
    _submit = "Reset"
    title = "Request account reset"
    email_old = EmailOldField()


class ResetForm(UserForm):
    _submit = "Reset"
    title = "Reset username and password"
    username = UsernameNewField("New username")
    password = PasswordNewField("New password")
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
