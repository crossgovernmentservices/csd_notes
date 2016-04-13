# -*- coding: utf-8 -*-
"""
Application configuration
"""

import os
from os.path import dirname, join


# get settings from environment, or credstash if running in AWS
env = os.environ
if env.get('SETTINGS') == 'AWS':
    from lib.aws_env import env


DEBUG = bool(env.get('DEBUG', True))

SECRET_KEY = env.get('SECRET_KEY', os.urandom(24))

SQLALCHEMY_DATABASE_URI = env.get(
    'DATABASE_URL',
    'sqlite:///{}'.format(join(dirname(__file__), '../development.db')))


# XXX Don't change the following settings unless necessary

# Skips concatenation of bundles if True, which breaks everything
ASSETS_DEBUG = False

ASSETS_LOAD_PATH = [
    'app/static',
    'app/templates']

# Calculate friendly times using UTC instead of local timezone
HUMANIZE_USE_UTC = True

MARKDOWN_EXTENSIONS = [
    'markdown.extensions.nl2br',
    'markdown.extensions.sane_lists',
    'markdown.extensions.smart_strong',
    'markdown.extensions.smarty',
]

# TODO this should be True when served via HTTPS
SESSION_COOKIE_SECURE = False

# Track modifications of objects and emit signals. Requires extra memory.
SQLALCHEMY_TRACK_MODIFICATIONS = False
