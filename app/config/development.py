# -*- coding: utf-8 -*-
"""
Development configuration settings
"""

import os


DEBUG = True

SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))

SESSION_COOKIE_SECURE = False


# local.py overrides all the common settings
try:
    from .local import *

except ImportError:
    pass
