# coding=utf-8
import requests_mock
from django.core.exceptions import ValidationError
from django.test import TestCase
from requests import HTTPError

from infra.apps.catalog.catalog_data_validator import CatalogDataValidator


class TestCatalogValidations(TestCase):
    validator = CatalogDataValidator()

    def test_submit_fails_when_url_and_file_are_empty(self):
        data_dict = {}
        with self.assertRaises(ValidationError):
            self.validator.get_and_validate_data(data_dict)

    def test_submit_fails_when_both_url_and_file_have_content(self):
        data_dict = {'file': "something", 'url': 'string'}
        with self.assertRaises(ValidationError):
            self.validator.get_and_validate_data(data_dict)

    @requests_mock.mock()
    def test_fails_when_response_is_not_successful(self, m):
        m.get('https://fake_url.com/data.json', text="Testing text", status_code=404)
        data_dict = {'format': 'json', 'identifier': 'test', 'url': 'https://fake_url.com/data.json'}
        with self.assertRaises(HTTPError):
            self.validator.get_and_validate_data(data_dict)

    @requests_mock.mock()
    def test_returns_correct_data_when_specifying_url(self, m):
        m.get('https://fake_url.com/data.json', text="Testing text")
        data_dict = {'format': 'json', 'identifier': 'test', 'url': 'https://fake_url.com/data.json'}
        data = self.validator.get_and_validate_data(data_dict)
        assert data['file'].read() == b"Testing text"

    def test_returns_correct_data_when_uploading_file(self):
        with open('infra/apps/catalog/tests/samples/simple.json', 'r+') as f:
            data_dict = {'format': 'json', 'identifier': 'test', 'file': f}
            data = self.validator.get_and_validate_data(data_dict)
            assert data['file'].read() == '{"identifier": "test"}'
