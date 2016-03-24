# -*- coding: utf-8 -*-
"""
Application configuration
"""

import os


# get settings from environment, or credstash if running in AWS
env = os.environ
if env.get('SETTINGS') == 'AWS':
    from lib.aws_env import env


DEBUG = env.get('DEBUG', True)

SECRET_KEY = env.get('SECRET_KEY', os.urandom(24))

SESSION_COOKIE_SECURE = False
