from flask import render_template
from flask.ext.wtf import Form
from wtforms import SubmitField, Label
from wtforms.validators import Required, Length
from wtforms.widgets import HTMLString

class BaseForm(Form):
    """
    Base class for all forms in the blog.
    """
    title = None
    _submit = None
    submit = SubmitField()

    def __init__(self, **kwargs):
        super(BaseForm, self).__init__(**kwargs)
        submit_label = self._submit or self.title or "Submit"
        self.submit.label = Label("submit", submit_label)

    def __call__(self, method="POST", action=None,
                 vertical=True, labelled=True):
        return render_template('form.html',
                               form=self,
                               method=method,
                               action=action,
                               vertical=vertical,
                               labelled=labelled)
