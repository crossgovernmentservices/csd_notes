from flask import url_for
import pytest

from tests.util import app  # noqa


@pytest.fixture
def response(client):
    return client.get(url_for('healthcheck.check_health'))


@pytest.mark.use_fixtures('response')
class TestWhenBrowsingToHealthcheckEndpoint(object):

    def test_it_exists(self, response):
        assert response.status_code == 200

    def test_it_reports_site_ok(self, response):
        assert response.json['site'] is True
