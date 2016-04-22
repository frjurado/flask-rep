from flask import current_app
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Regexp, Email, EqualTo, \
        ValidationError, StopValidation
from ..models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


# custom fields
# ---------------------------------------------------------
class EmailField(StringField):
    def __init__(
            self,
            label="Email",
            validators=[Required(),Email()],
            **kwargs):
        super(EmailField, self).__init__(label=label,validators=validators,**kwargs)

class UsernameOldField(StringField):
    def __init__(self, label="Username", validators=[Required()], **kwargs):
        super(UsernameOldField, self).__init__(label=label,validators=validators,**kwargs)

class UsernameNewField(StringField):
    def __init__(
            self,
            label="Username",
            validators=[Required(),Length(1,64),
                Regexp('[A-Za-z0-9_.]+',0,
                "Username must only have letters, numbers, dots and underscores."
            )],
            **kwargs):
        super(UsernameNewField, self).__init__(label=label,validators=validators,**kwargs)

class PasswordOldField(PasswordField):
    def __init__(self, label="Password", validators=[Required()], **kwargs):
        super(PasswordOldField, self).__init__(label=label,validators=validators,**kwargs)

class PasswordNewField(PasswordField):
    def __init__(
            self,
            label="Password",
            validators=[Required(),Length(8,64),
                Regexp('[A-Za-z0-9_.]+',0,
                "Password must only have letters, numbers, dots and underscores."
                # you should really check it has them all?
            )],
            **kwargs):
        super(PasswordNewField, self).__init__(label=label,validators=validators,**kwargs)

class VerifyField(PasswordField):
    def __init__(
            self,
            label="Confirm password",
            validators=[Required(),EqualTo('password', "Passwords don't match.")],
            **kwargs):
        super(VerifyField, self).__init__(label=label,validators=validators,**kwargs)


# main forms
# ---------------------------------------------------------
class SignupForm(Form):
    heading = "Sign up"

    email = EmailField()
    username = UsernameNewField()
    password = PasswordNewField()
    verify = VerifyField()
    submit = SubmitField("Sign up")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already in use.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")


class LoginForm(Form):
    heading = "Log in"

    username = UsernameOldField()
    password = PasswordOldField()
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log in")

    def __init__(self, **kwargs):
        super(LoginForm, self).__init__(**kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user and user.is_member() and user.verify_password(self.password.data):
            self.user = user
            return True
        else:
            self.password.errors.append("Invalid username or password.")
            return False


# change data forms
# ---------------------------------------------------------
class ChangeForm(Form):
    submit = SubmitField("Change")

    def __init__(self, user, **kwargs):
        super(ChangeForm, self).__init__(**kwargs)
        self.user = user

class ChangeEmailForm(ChangeForm):
    heading = "Change email"

    email = EmailField("New email")
    password = PasswordOldField()

    def validate_email(self, field):
        if field.data == self.user.email:
            raise ValidationError("That's already your email.")
        elif User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already in use.")

    def validate_password(self, field):
        if not self.user.verify_password(field.data):
            raise ValidationError("Invalid password.")


class ChangeUsernameForm(ChangeForm):
    heading = "Change username"

    username = UsernameNewField("New username")
    password = PasswordOldField()

    def validate_username(self, field):
        if field.data == self.user.username:
            raise ValidationError("That's already your username.")
        elif User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")

    def validate_password(self, field):
        if not self.user.verify_password(field.data):
            raise ValidationError("Invalid password.")


class ChangePasswordForm(ChangeForm):
    heading = "Change password"

    password = PasswordOldField("Old password")
    password_new = PasswordNewField("New password")
    verify_new = VerifyField(
        "Verify new password",
        validators=[Required(),EqualTo('password_new', "Passwords don't match.")]
    )

    def validate_password(self, field):
        if not self.user.verify_password(field.data):
            raise ValidationError("Invalid password.")

# reset forms
# ---------------------------------------------------------
class ResetRequestForm(Form):
    heading = "Request account reset"

    email = EmailField()
    submit = SubmitField('Reset')

    def __init__(self, **kwargs):
        super(ResetRequestForm, self).__init__(**kwargs)
        self.user = None

    def validate_email(self, field):
        self.user = User.query.filter_by(email=field.data).first()
        if self.user is None:
            raise ValidationError("Unknown email address.")


class ResetForm(Form):
    heading = "Reset username and password"

    email = EmailField("Enter your email again, please")
    username = UsernameNewField("New username")
    password = PasswordNewField("New password")
    verify = VerifyField()
    submit = SubmitField('Reset password')

    def __init__(self, token, **kwargs):
        super(ResetForm, self).__init__(**kwargs)
        self.user = None
        self.token = token

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        self.user = User.query.filter_by(email=self.email.data).first()
        if self.user is None or not self.user.is_member():
            self.email.errors.append("Invalid email.")
            return False
        if self.username.data != self.user.username and \
                User.query.filter_by(username=self.username.data).first():
            self.username.errors.append("Username already in use.")
            return False
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(self.token)
        except:
            self.email.errors.append("Invalid token.")
            return False
        if self.user != User.query.get(data.get('reset')):
            self.email.errors.append("Invalid token.")
            return False
        return True
