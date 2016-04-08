from flask import url_for
import pytest
import requests


@pytest.mark.use_fixtures('live_server')
class WhenApplicationIsUp(object):

    def it_returns_HTTP_200_for_the_index_page(self, live_server):
        r = requests.get(url_for('base.index', _external=True))
        assert 200 == r.status_code
