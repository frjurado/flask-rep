from flask import Markup, render_template, url_for
from flask.ext.wtf import Form
from wtforms import SubmitField, Label


class BaseForm(Form):
    """
    Base class for all forms in the blog.
    """
    _vertical = True
    _labelled = True
    _small = False
    _danger = False

    _endpoint = None
    _endpoint_kwargs = {}
    _submit = None
    title = None
    submit = SubmitField()

    _enctype = None

    def __init__(self, **kwargs):
        super(BaseForm, self).__init__(**kwargs)
        submit_label = self._submit or self.title or "Submit"
        self.submit.label = Label("submit", submit_label)

    def _action(self):
        if self._endpoint is not None:
            return url_for(self._endpoint, **self._endpoint_kwargs)
        return None

    def __call__(self, method="POST", action=None, enctype=None,
                 vertical=None, labelled=None, small=None, danger=None):
        action = action or self._action()
        enctype = enctype or self._enctype
        vertical = vertical or self._vertical
        labelled = labelled or self._labelled
        small = small or self._small
        danger = danger or self._danger
        return Markup( render_template( 'form.html',
                                        form = self,
                                        method = method,
                                        action = action,
                                        enctype = enctype,
                                        vertical = vertical,
                                        labelled = labelled,
                                        small = small ,
                                        danger = danger ) )
