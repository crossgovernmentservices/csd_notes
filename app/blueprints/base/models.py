# -*- coding: utf-8 -*-
"""
Base models
"""

from flask.ext.security import RoleMixin, UserMixin
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from app.extensions import db
from lib.model_utils import GetOr404Mixin, GetOrCreateMixin


user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin, GetOrCreateMixin, GetOr404Mixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String)
    full_name = db.Column(db.String)
    inbox_email = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship(
        'Role',
        secondary=user_roles,
        backref=db.backref('users', lazy='dynamic'))

    @classmethod
    def get_or_create(cls, **kwargs):
        try:
            user = User.query.filter_by(**kwargs).one()

        except NoResultFound:
            user = User(**kwargs)
            db.session.add(user)
            db.session.commit()

        except MultipleResultsFound:
            raise

        return user
