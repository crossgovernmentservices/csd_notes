# -*- coding: utf-8 -*-
"""
OIDC client Flask extension
"""

from urllib.parse import urlencode

from flask import url_for
from jose import jwt
import requests


def verify_id_token(token, config):
    header = jwt.get_unverified_header(token)
    key = [key for key in config['keys'] if key['kid'] == (header['kid'])]
    return jwt.decode(token, key[0], audience=config['client_id'])


class OIDC(object):
    """
    Flask extension which provides a simple API for OIDC authentication
    """

    def __init__(self, app=None):
        self._callback_fn = None
        self._config = {}
        if app:
            self.init_app(app)

    def init_app(self, app):
        self._app = app
        self._config = dict(app.config['OIDC_PROVIDERS'])

    def callback(self, fn):
        """
        Decorate a Flask view function to set as the OIDC callback handler
        """

        self._callback_fn = fn
        return fn

    @property
    def callback_url(self):
        """
        The OIDC callback/redirect URI
        """

        flipped_view_fns = {v: k for k, v in self._app.view_functions.items()}
        view_name = flipped_view_fns[self._callback_fn]
        return url_for(view_name, _external=True)

    def openid_config(self, provider_name):
        """
        Retrieve OpenID configuration for the specified IdP
        """

        config = self._config.get(provider_name, {})

        if 'authorization_endpoint' not in config:

            config.update(requests.get(
                '{}/.well-known/openid-configuration'.format(
                    config['discovery_url'])).json())

            if 'jwks_uri' in config:
                config.update(requests.get(
                    config['jwks_uri']).json())

            self._config[provider_name] = config

        return config

    def login(self, provider_name):
        """
        Generate a login URL for a provider
        """

        config = self.openid_config(provider_name)

        auth_request = AuthenticationRequest(
            scope='openid email profile',
            response_type='code',
            client_id=config['client_id'],
            redirect_uri=config.get('redirect_uri', self.callback_url))

        return auth_request.url(config['authorization_endpoint'])

    def authenticate(self, provider_name, request):
        """
        Authenticate a user and retrieve their userinfo
        """

        config = self.openid_config(provider_name)
        auth_code = request.args['code']

        token_response = self.token_request(config, auth_code)

        access_token = token_response['access_token']

        claims = verify_id_token(token_response['id_token'], config)

        claims.update(self.userinfo(config, access_token))

        return claims

    def token_request(self, config, auth_code):
        """
        Exchange provider auth code for an ID Token and an Access Token
        """

        request = TokenRequest(
            grant_type='authorization_code',
            code=auth_code,
            redirect_uri=config.get('redirect_uri', self.callback_url),
            client_id=config['client_id'],
            secret=config['client_secret'])

        response = request.send(config['token_endpoint'])

        if 'error' in response:
            raise Exception(response['error'])

        return response

    def userinfo(self, config, access_token):
        """
        Get userinfo Claims from the provider using an Access Token
        """

        if 'userinfo_endpoint' not in config:
            return {}

        request = UserInfoRequest(access_token)

        return request.send(config['userinfo_endpoint'])


class AuthenticationRequest(object):

    def __init__(self, scope, response_type, client_id, redirect_uri, **kw):
        if 'openid' not in scope:
            scope = 'openid {}'.format(scope)

        self._params = {
            'redirect_uri': redirect_uri,
            'response_type': response_type,
            'client_id': client_id,
            'scope': scope
        }

        self._params.update(kw)

    def url(self, auth_endpoint):
        params = urlencode(self._params)
        return '{}?{}'.format(auth_endpoint, params)


class TokenRequest(object):

    def __init__(self, grant_type, code, redirect_uri, client_id, secret):
        self.client_id = client_id
        self.client_secret = secret
        self._params = {
            'redirect_uri': redirect_uri,
            'code': code,
            'grant_type': grant_type}

    def send(self, token_endpoint):
        response = requests.post(
            token_endpoint,
            data=urlencode(self._params),
            auth=(self.client_id, self.client_secret),
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        return response.json()


class UserInfoRequest(object):

    def __init__(self, access_token):
        self.access_token = access_token

    def send(self, userinfo_endpoint):
        response = requests.get(
            userinfo_endpoint,
            headers={'Authorization': 'Bearer {token}'.format(
                token=self.access_token)})
        return response.json()
