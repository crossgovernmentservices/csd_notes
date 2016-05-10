from unittest.mock import patch

import pytest

from app.factory import create_app


@pytest.yield_fixture
def credstash():
    with patch('lib.aws_env.env.__getitem__') as get:
        get.return_value = 'fetched from credstash'
        yield


@pytest.yield_fixture
def aws_env():
    with patch.dict('os.environ', SETTINGS='AWS'):
        yield


@pytest.yield_fixture
def test_app(app, db, credstash, aws_env):
    app_backup = app
    yield create_app()
    app = app_backup
    db.app = app


class WhenDeployedInAWS(object):

    def it_fetches_secrets_from_credstash(self, test_app):
        assert test_app.config['SECRET_KEY'] == 'fetched from credstash'
