from flask import url_for
import pytest


@pytest.fixture
def response(client):
    return client.get(url_for('base.index'))


class WhenRenderingAPage(object):

    def it_uses_govuk_elements(self, response):
        assert '/static/stylesheets/govuk_elements.css' in \
            response.get_data(as_text=True)
