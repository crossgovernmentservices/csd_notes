from flask import url_for
import pytest


@pytest.fixture
def response(client):
    return client.get(url_for('healthcheck.check_health'))


class WhenBrowsingToHealthcheckEndpoint(object):

    def it_exists(self, response):
        assert response.status_code == 200

    def it_reports_site_ok(self, response):
        assert response.json['site'] is True
