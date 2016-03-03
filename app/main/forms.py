from flask.ext.wtf import Form
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import Required, Length


class NameForm(Form):
    name = StringField(
        'Name',
        validators=[ Required(), Length(min=4) ]
    )
    role = RadioField(
        'Job',
        choices=[ ('campesino', 'Campesino'), ('ganadero', 'Ganadero') ],
        validators=[ Required() ]
    )
    submit = SubmitField('Submit')
