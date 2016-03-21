# -*- coding: utf-8 -*-
"""
Configuration settings
"""

import os


# select source of environment vars
env = os.environ
if env.get('SETTINGS') == 'aws':
    from .aws import AWSIntanceEnv
    env = AWSIntanceEnv()


DEBUG = env.get('DEBUG', True)

SECRET_KEY = env.get('SECRET_KEY', os.urandom(24))

SESSION_COOKIE_SECURE = False


# local.py overrides all the common settings
try:
    from .local import *

except ImportError:
    pass
