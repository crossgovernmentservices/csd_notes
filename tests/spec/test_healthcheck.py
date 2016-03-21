import json
import unittest

from tests.util import test_app


class TestHealthCheck(unittest.TestCase):

    def setUp(self):
        self.app = test_app()
        self.response = self.app.get('/healthcheck.json')

    def test_healthcheck_endpoint_exists(self):
        self.assertEqual(200, self.response.status_code)

    def test_healthcheck_site_status(self):
        status = json.loads(self.response.get_data(as_text=True))
        self.assertTrue(status['site'])
