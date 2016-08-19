# -*- coding: utf-8 -*-
from flask import url_for
from wtforms import StringField, SelectField, HiddenField
from wtforms.validators import InputRequired, URL, ValidationError
from ..forms import InlineForm
from ..models.users import Role, User


class UserForm(InlineForm):
    _endpoint = 'user.edit_profile'
    username = HiddenField(validators=[InputRequired()])

    def __init__(self, user=None, **kwargs):
        super(UserForm, self).__init__(**kwargs)
        if user is not None:
            self.username.data = user.username
            self._endpoint_kwargs = {'username': self.username.data}

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user is None:
            raise ValidationError(u"Invalid user.")
        self.user = user


class NameForm(UserForm):
    _submit = u"Change name"
    name = StringField(u"Name", validators = [InputRequired()])


class UrlForm(UserForm):
    _submit = u"Change URL"
    url = StringField(u"URL", validators = [InputRequired(), URL()])


class DeleteForm(UserForm):
    _danger = True
    _submit = u"Delete account"
    _endpoint = 'user.delete_account'


class RoleForm(UserForm):
    _submit = u"Change role"
    _endpoint = 'user.assign_role'
    role = SelectField("Role", coerce=int, validators=[InputRequired()])

    def __init__(self, user=None, **kwargs):
        super(RoleForm, self).__init__(user, **kwargs)
        self.role.choices = [
            (role.id, role.name)
            for role in Role.query.order_by(Role.permissions).all()
        ]
        self.role.data = self.role.data or user.role.id

    def validate_role(self, field):
        if not self.user.set_role(field.data):
            raise ValidationError(u"Invalid role.")
