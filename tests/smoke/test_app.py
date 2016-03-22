from flask import url_for
import pytest
import requests

from tests.util import app  # noqa


@pytest.mark.use_fixtures('live_server')
class TestApplication(object):

    def test_app_ready(self, live_server):
        r = requests.get(url_for('base.index', _external=True))
        assert 200 == r.status_code
