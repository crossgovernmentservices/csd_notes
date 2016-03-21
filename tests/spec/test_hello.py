import unittest

from tests.util import test_app


class TestHello(unittest.TestCase):

    def setUp(self):
        self.app = test_app()

    def test_hello_world(self):
        r = self.app.get('/')
        assert 'Hello World!' in str(r.get_data())
