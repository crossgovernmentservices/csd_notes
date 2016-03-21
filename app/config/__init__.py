# -*- coding: utf-8 -*-
"""
Configuration settings
"""

import os


env = os.environ


DEBUG = env.get('DEBUG', True)

SECRET_KEY = env.get('SECRET_KEY', os.urandom(24))

SESSION_COOKIE_SECURE = False


# local.py overrides all the common settings
try:
    from .local import *

except ImportError:
    pass
