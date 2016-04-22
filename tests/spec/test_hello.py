from flask import url_for
import pytest


@pytest.fixture
def response(client):
    return client.get(url_for('base.index'))


class WhenBrowsingToIndexPage(object):

    def it_shows_hello_world(self, response):
        assert 'Civil Service Digital' in response.get_data(as_text=True)
