import unittest

from app.factory import create_app


class TestHello(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app = self.app.test_client()

    def test_hello_world(self):
        r = self.app.get('/')
        assert 'Hello World!' in str(r.data)
