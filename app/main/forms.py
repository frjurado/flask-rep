from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Length

class NameForm(Form):
    name = StringField('Name', validators=[Required(), Length(min=4)])
    submit = SubmitField('Submit')
