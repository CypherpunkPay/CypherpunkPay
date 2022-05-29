from typing import Optional

import pytest
import webtest

import cypherpunkpay

from tests.unit.test_case import CypherpunkpayTestCase


@pytest.mark.usefixtures('instantiate_app')
@pytest.mark.usefixtures('acceptance_per_function_wrapper')
class CypherpunkpayAcceptanceTestCase(CypherpunkpayTestCase):

    # Cypherpunkpay application
    app: cypherpunkpay.App = None

    # WSGI web application
    webapp: Optional[webtest.TestApp] = None

    def assertInBody(self, response, expected_content: str):
        self.assertIn(expected_content, response.text)

    def assertNotInBody(self, response, expected_content: str):
        self.assertNotIn(expected_content, response.text)

    def login(self):
        self.webapp.post(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/login', [
            ('username', 'admin'),
            ('password', 'admin123')
        ], status=302)   # make sure login successful
