import unittest
from app import app
from config import config

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        app.config.from_object(config['testing'])
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(app is None)

    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])
