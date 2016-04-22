# -*- coding: utf-8 -*-
"""
Single Sign-On views
"""

from flask import (
    Blueprint,
    redirect,
    request,
    url_for
)
from flask.ext.security.utils import login_user, logout_user

from app.extensions import (
    user_datastore,
    oidc
)


sso = Blueprint('sso', __name__)


@sso.route('/login/<idp>')
@sso.route('/login')
def login(idp='dex'):
    "login redirects to Dex for SSO login/registration"
    return redirect(oidc.login(idp))


@sso.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base.index'))


@sso.route('/auth/<idp>/callback')
@sso.route('/callback')
@oidc.callback
def oidc_callback(idp='dex'):
    user_info = oidc.authenticate(idp, request)

    user = user_datastore.get_user(user_info['email'])

    if not user:
        user = create_user(user_info)

    login_user(user)

    if 'next' in request.args:
        return redirect(request.args['next'])

    return redirect(url_for('base.index'))


def create_user(user_info):
    email = user_info['email']
    name = user_info.get('nickname', user_info.get('name'))

    user = add_role('USER', user_datastore.create_user(
        email=email,
        full_name=name))

    user_datastore.commit()

    return user


def add_role(role, user):
    user_role = user_datastore.find_or_create_role(role)
    user_datastore.add_role_to_user(user, user_role)
    return user
