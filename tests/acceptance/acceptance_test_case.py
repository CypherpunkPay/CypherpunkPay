import webtest

import cypherpunkpay
from cypherpunkpay.common import *

from tests.unit.test_case import CypherpunkpayTestCase


class CypherpunkpayAcceptanceTestCase(CypherpunkpayTestCase):

    # Cypherpunkpay application
    app: cypherpunkpay.App = None

    # WSGI web application
    webapp: webtest.TestApp = None

    def assertInBody(self, response, expected_content: str):
        self.assertIn(expected_content, response.text)

    def assertNotInBody(self, response, expected_content: str):
        self.assertNotIn(expected_content, response.text)

    def login(self):
        self.webapp.post(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/login', [
            ('username', 'admin'),
            ('password', 'admin123')
        ], status=302)   # make sure login successful
