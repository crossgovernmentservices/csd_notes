import os

from flask.ext.migrate import upgrade
import pytest

from app.factory import create_app


@pytest.fixture(scope='session')
def app(request):
    test_db = os.path.join(os.path.dirname(__file__), '../test.db')
    test_db_uri = 'sqlite:///{}'.format(test_db)
    app = create_app(
        TESTING=True,
        TEST_DB_PATH=test_db,
        SQLALCHEMY_DATABASE_URI=test_db_uri)

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):

    def remove_db():
        if os.path.exists(app.config['TEST_DB_PATH']):
            os.unlink(app.config['TEST_DB_PATH'])

    remove_db()

    # run migrations
    upgrade()

    request.addfinalizer(remove_db)

    return app.extensions['sqlalchemy'].db
