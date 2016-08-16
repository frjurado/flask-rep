# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declared_attr
from flask import Markup
from .. import db


class BaseModel(db.Model):
    """
    The base class for all models in the blog.
    """
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return self._get_name()
        # return "<{0}: {1}>".format(self.__class__.__name__, self._get_name())

    def _get_name(self):
        try:
            return self.name
        except:
            return str(self.id)

    def _href(self):
        raise NotImplementedError()

    def link(self, classes=None):
        return Markup(
            u"<a class='{2}' href={1}>{0}</a>".format(
                self._get_name(),
                self._href(),
                classes or ""
            )
        )
