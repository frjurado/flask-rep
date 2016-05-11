from flask.ext.login import current_user
from flask.ext.wtf import Form
from wtforms import HiddenField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, Label
from wtforms.widgets import HiddenInput
from wtforms.validators import Required, Length, Regexp, Email, EqualTo, \
        ValidationError, StopValidation
from flask.ext.pagedown.fields import PageDownField
from ..models import Permission, Role, User


class AdminUsersForm(Form):
    username = HiddenField(validators=[Required()])
    submit = SubmitField()

    def __init__(self, formdata=None, user=None, submit_label="Submit", **kwargs):
        super(AdminUsersForm, self).__init__(formdata, **kwargs)
        if user:
            self.username.data = user.username
            self.submit.label = Label('submit', submit_label)


class AssignRoleForm(AdminUsersForm):
    role = SelectField("Role", coerce=int, validators=[Required()], default=3)

    def __init__(self, formdata=None, user=None, **kwargs):
        super(AssignRoleForm, self).__init__(formdata, user, "Assign", **kwargs)
        self.role.choices = [
            (role.id, role.name)
            for role in Role.query.order_by(Role.permissions).all()
            if role.member and role.permissions != 0xfd ]
        if user:
            self.username.data = user.username
            self.role.data = user.role.id

    def validate_username(self, field):
        self.user = User.query.filter_by(username=field.data).first()
        if self.user is None:
            raise StopValidation("Invalid user")
        elif self.user == current_user:
            raise StopValidation("You can't change your own role")

    def validate_role(self, field):
        self.role = Role.query.get(field.data)
        if not self.role:
            raise StopValidation("Invalid role.")
        elif self.user.role == self.role:
            raise StopValidation("That was already his/her role.")


class BanishUserForm(AdminUsersForm):
    def __init__(self, formdata=None, user=None, **kwargs):
        super(BanishUserForm, self).__init__(formdata, user, "Banish", **kwargs)

    def validate_username(self, field):
        self.user = User.query.filter_by(username=field.data).first()
        if self.user is None:
            raise ValidationError("Invalid user")
        elif not self.user.is_member() or self.user.is_main_administrator():
            raise ValidationError("You can't banish this user.")


class BlockUserForm(AdminUsersForm):
    def __init__(self, formdata=None, user=None, **kwargs):
        super(BlockUserForm, self).__init__(formdata, user, "Block", **kwargs)

    def validate_username(self, field):
        self.user = User.query.filter_by(username=field.data).first()
        if self.user is None:
            raise ValidationError("Invalid user")
        elif self.user.role.permissions != 0x01:
            raise ValidationError("You can't block a non-guest.")


class UnblockUserForm(AdminUsersForm):
    def __init__(self, formdata=None, user=None, **kwargs):
        super(UnblockUserForm, self).__init__(formdata, user, "Unblock", **kwargs)

    def validate_username(self, field):
        self.user = User.query.filter_by(username=field.data).first()
        if self.user is None:
            raise ValidationError("Invalid user")
        elif self.user.role.permissions != 0:
            raise ValidationError("User wasn't blocked.")


class DeleteAccountForm(AdminUsersForm):
    def __init__(self, formdata=None, user=None, **kwargs):
        super(DeleteAccountForm, self).__init__(formdata, user, "Delete", **kwargs)

    def validate_username(self, field):
        self.user = User.query.filter_by(username=field.data).first()
        if self.user is None:
            raise ValidationError("Invalid user")
        elif self.user.role.permissions != 0:
            raise ValidationError("You can only delete a blocked account.")


class EditUserProfileForm(Form):
    name = StringField("Name")
    url = StringField("Url")
    newsletter = BooleanField("Do you want to receive our newsletter?")
    submit = SubmitField("Save changes")


######################################
class PostForm(Form):
    name = StringField("Title", validators=[Required()])
    excerpt = TextAreaField("Excerpt", validators=[Required()])
    body = PageDownField("Body", validators=[Required()])
    submit = SubmitField("Submitir :P")
