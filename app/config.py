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


ASSETS_DEBUG = False

DEBUG = bool(env.get('DEBUG', True))

HUMANIZE_USE_UTC = True

SECRET_KEY = env.get('SECRET_KEY', os.urandom(24))

SESSION_COOKIE_SECURE = False

SQLALCHEMY_DATABASE_PATH = join(dirname(__file__), '../development.db')

SQLALCHEMY_DATABASE_URI = env.get(
    'DATABASE_URI',
    'sqlite:///{}'.format(SQLALCHEMY_DATABASE_PATH))

SQLALCHEMY_TRACK_MODIFICATIONS = bool(env.get(
    'SQLALCHEMY_TRACK_MODIFICATIONS',
    False))

TESTING = bool(env.get('TESTING', False))
