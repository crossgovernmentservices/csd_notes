from functools import wraps
import ipdb
import sys
import traceback

from app.factory import create_app


def test_app(config=None):
    app = create_app(config)
    app.config['TESTING'] = True
    return app.test_client()


def debug_on(*exceptions):

    if not exceptions:
        exceptions = (AssertionError,)

    def decorator(f):

        @wraps(f)
        def wrapper(*args, **kwargs):

            try:
                return f(*args, **kwargs)

            except exceptions:
                info = sys.exc_info()
                traceback.print_exception(*info)
                ipdb.post_mortem(info[2])

        return wrapper

    return decorator
