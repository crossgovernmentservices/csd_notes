import subprocess

from flask_migrate import upgrade
import pytest
import sqlalchemy

from app.blueprints.base.models import User
from app.config import SQLALCHEMY_DATABASE_URI
from app.extensions import db as _db
from app.factory import create_app


TEST_DATABASE_URI = SQLALCHEMY_DATABASE_URI + '_test'


@pytest.yield_fixture(scope='session')
def app(request):
    app = create_app(TESTING=True, SQLALCHEMY_DATABASE_URI=TEST_DATABASE_URI)

    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


def reset_migrations(db):

    # reset migrations, otherwise they will not be reapplied
    conn = db.engine.connect()

    try:
        conn.execute('DELETE FROM alembic_version')

    except sqlalchemy.exc.ProgrammingError:
        pass

    finally:
        conn.close()


def teardown_db(db):
    db.drop_all()
    reset_migrations(db)


def init_db(dbname, db):
    sqlalchemy.orm.configure_mappers()

    try:
        teardown_db(db)

    except sqlalchemy.exc.OperationalError as e:
        if 'does not exist' in str(e):
            create_db(dbname)
            init_db(dbname, db)

    upgrade()


def create_db(dbname):
    subprocess.call(['/usr/bin/env', 'createdb', dbname], timeout=1)


@pytest.yield_fixture(scope='session')
def db(request, app):
    _db.app = app
    _, dbname = TEST_DATABASE_URI.rsplit('/', 1)

    init_db(dbname, _db)

    yield _db

    teardown_db(_db)


@pytest.yield_fixture(scope='function')
def db_session(db, request):
    connection = db.engine.connect()
    transaction = connection.begin()

    session_factory = sqlalchemy.orm.sessionmaker(bind=connection)
    db.session = session = sqlalchemy.orm.scoped_session(session_factory)

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def selenium(db, live_server, selenium):
    """Override selenium fixture to always use flask live server"""
    return selenium


@pytest.fixture
def test_user(db_session):
    user = User(email='test@example.com', full_name='Test Test', active=True)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.yield_fixture
def logged_in(test_user, client):

    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True

    yield test_user

    with client.session_transaction() as session:
        del session['user_id']
        del session['_fresh']
