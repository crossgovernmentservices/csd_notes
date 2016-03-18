import unittest

from .functest_app import TestApplication


class FuncTests(unittest.TestSuite):

    def __init__(self):
        self.addTests(TestApplication)
