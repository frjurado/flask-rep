from flask import Markup, render_template, url_for
from flask.ext.wtf import Form
from wtforms import SubmitField, Label
from wtforms.widgets.core import html_params


class _Form(Form):
    """
    Super-class for all forms in the blog.
    """
    _modal = False
    _inline = False
    _danger = False

    _endpoint = None
    _endpoint_kwargs = None
    _method = "POST"
    _enctype = None
    _form_classes = []

    _submit = None
    _title = None
    submit = SubmitField()


    def __init__(self, **kwargs):
        super(_Form, self).__init__(**kwargs)
        submit_label = self._submit or self._title or "Submit"
        self.submit.label = Label("submit", submit_label)

    def _id(self):
        name = self.__class__.__name__
        return name[0].lower() + name[1:]

    def _action(self):
        if self._endpoint is not None and self._endpoint_kwargs is not None:
            return url_for(self._endpoint, **self._endpoint_kwargs) # **?
        elif self._endpoint is not None:
            return url_for(self._endpoint)
        return None

    def _classes(self):
        if self._form_classes is not None:
            return ' '.join(self._form_classes)
        return None

    def __html__(self):
        return self()

    def __call__(self, classes=None):
        return Markup( render_template( 'form.html',
                                        form = self) )


class BaseForm(_Form):
    pass


class ModalForm(_Form):
    _modal = True


class InlineForm(_Form):
    _inline = True
    _form_classes = ['form-inline']
