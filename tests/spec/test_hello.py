from flask import url_for
import pytest

from tests.util import app  # noqa


@pytest.fixture
def response(client):
    return client.get(url_for('base.index'))


@pytest.mark.use_fixtures('response')
class TestWhenBrowsingToIndexPage(object):

    def test_it_shows_hello_world(self, response):
        assert 'Hello World!' in response.get_data(as_text=True)
