# -*- coding: utf-8 -*-
"""
Single Sign-On views
"""

from urllib.parse import urlparse, urlunparse

from flask import (
    Blueprint,
    redirect,
    request,
    session,
    url_for
)
from flask.ext.security.utils import login_user, logout_user

from app.extensions import (
    user_datastore,
    oidc
)


sso = Blueprint('sso', __name__)


def sanitize_url(url):

    if url:
        parts = list(urlparse(url))
        parts[0] = ''
        parts[1] = ''
        parts[3] = ''
        url = urlunparse(parts[:6])

    return url


@sso.route('/login/<idp>')
@sso.route('/login')
def login(idp='dex'):
    "login redirects to Dex for SSO login/registration"

    next_url = sanitize_url(request.args.get('next'))
    if next_url:
        session['next_url'] = next_url

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

    next_url = session.pop('next_url', url_for('base.index'))

    return redirect(next_url)


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
