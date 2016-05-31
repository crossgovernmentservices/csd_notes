# -*- coding: utf-8 -*-
"""
Tests for OIDC client
"""

import contextlib
import mock
from urllib.parse import parse_qs, urlparse

from flask import url_for
from flask_login import current_user, logout_user
import pytest

from app.blueprints.base.models import User
from app.extensions import oidc


@pytest.yield_fixture
def idp():
    mock_config = {
        'dex': {
            'client_id': 'mock_id',
            'client_secret': 'mock_secret',
            'discovery_url': 'https://example.com',
            'authorization_endpoint': 'https://example.com/auth',
            'token_endpoint': 'https://example.com/token'}}

    with mock.patch.dict('app.blueprints.sso.views.oidc._config', mock_config):
        with mock.patch('lib.oidc.TokenRequest') as TokenRequest:

            TokenRequest.return_value.send.return_value = {
                'access_token': 'dummy_access_token',
                'id_token': 'dummy_id_token'}

            yield


@contextlib.contextmanager
def id_token_patch(user):
    with mock.patch('lib.oidc.verify_id_token') as verify:
        verify.return_value = {
            'email': user.email,
            'name': user.full_name}
        yield


@pytest.yield_fixture
def new_user(idp):

    user = User(
        email='test_user@example.com',
        full_name='Test User 1')

    with id_token_patch(user):
        yield user


@pytest.yield_fixture
def existing_user(idp, db_session):

    user = User(
        email='test_user_2@example.com',
        full_name='Test User 2',
        active=True)

    db_session.add(user)
    db_session.commit()

    with id_token_patch(user):
        yield user


@pytest.fixture
def login(client, idp):
    return client.get(url_for('sso.login'))


@pytest.fixture
def logged_out(app):
    logout_user()


@pytest.fixture
def callback(client, db_session, logged_out):
    return client.get(
        oidc.callback_url,
        query_string='code=dummy_code',
        follow_redirects=True)


class WhenLoggingInViaOIDC(object):

    def it_redirects_to_the_specified_idp_auth_endpoint(self, login):
        assert login.status_code == 302

        auth_url = login.headers['Location']
        assert oidc.login('dex') in auth_url
        assert 'response_type=code' in auth_url

        args = parse_qs(urlparse(auth_url)[4])
        assert args['redirect_uri'][0] == oidc.callback_url

    def it_logs_in_an_authorized_new_user(self, new_user, callback):
        assert current_user.email == new_user.email

    def it_logs_in_an_authorized_existing_user(self, existing_user, callback):
        assert current_user == existing_user
