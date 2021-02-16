#!/usr/bin/env python
"""Test for main
"""
from unittest import TestCase

from main import db_connection, get_website_data, execute_consult, save_content


class TestMain(unittest.TestCase):
    @unittest.mock('main.mysql.connector.connect')
    def test_connection(self, mockconnect):
        db_connection()
        mockconnect.assert_called()

    # Verify that the website is responding something
    def test_get_website_data(self):
        self.assertTrue(get_website_data('https://time.is/es/Argentina'))

    # Verify
    def test_execute_consult(self):
        execute_consult()


    def test_save_content(self):
        save_content()
