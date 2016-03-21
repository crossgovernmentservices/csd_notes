from flask_testing import LiveServerTestCase
import random
import requests

from app.factory import create_app


class TestApplication(LiveServerTestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        # XXX - may result in "OSError: [Errno 48] Address already in use"
        #       if the same port number is used in quick succession
        app.config['LIVESERVER_PORT'] = random.randint(8000, 8999)
        return app

    def test_app_ready(self):
        r = requests.get(self.get_server_url())
        self.assertEqual(200, r.status_code)
