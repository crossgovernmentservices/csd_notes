# -*- coding: utf-8 -*-
"""
Basic Auth middleware
"""

from base64 import b64decode
import os


class BasicAuth(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):

        if self.authenticated(environ.get('HTTP_AUTHORIZATION')):
            return self.app(environ, start_response)

        return self.login(environ, start_response)

    def authenticated(self, header):

        if not header:
            return False

        _, encoded = header.split(None, 1)
        decoded = b64decode(encoded).decode('UTF-8')
        username, password = decoded.split(':', 1)
        return username == os.environ['BASIC_AUTH_USER'] and \
            password == os.environ['BASIC_AUTH_PASSWORD']

    def login(self, environ, start_response):
        start_response(
            '401 Authentication Required',
            [
                ('Content-Type', 'text/html'),
                ('WWW-Authenticate', 'Basic realm="Login"')])
        return [b'Login']
