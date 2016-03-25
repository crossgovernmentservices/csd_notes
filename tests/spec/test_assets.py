from flask import url_for
import pytest

from tests.util import app  # noqa


@pytest.fixture
def response(client):
    return client.get(url_for('base.index'))


@pytest.mark.use_fixtures('response')
class TestWhenRenderingAPage(object):

    def test_it_uses_govuk_elements(self, response):
        assert '/static/stylesheets/govuk_elements.css' in \
            response.get_data(as_text=True)
