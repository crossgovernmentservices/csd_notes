from flask_testing import LiveServerTestCase
import requests

from app.factory import create_app


class TestApplication(LiveServerTestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 8901
        return app

    def test_app_ready(self):
        r = requests.get(self.get_server_url())
        self.assertEqual(200, r.status_code)
