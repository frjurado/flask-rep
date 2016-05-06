from flask.ext.wtf import Form
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import Required, Length
from wtforms.widgets import HTMLString


class InlineButtonWidget(object):
    html = '<button type="submit" class="btn btn-default">{}</button>'

    def __init__(self, input_type='submit'):
        self.input_type = input_type

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return HTMLString(self.html.format(field.label))


class ButtonSubmitField(BooleanField):
    """
    Represents an ``<button type="submit">``.
    This allows checking if a given submit button has been pressed.
    """
    widget = InlineButtonWidget()
