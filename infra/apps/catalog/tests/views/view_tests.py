# coding=utf-8
import requests_mock
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from requests import HTTPError

from infra.apps.catalog.catalog_data_validator import CatalogDataValidator
from infra.apps.catalog.models import Catalog


class TestCatalogValidations(TestCase):
    validator = CatalogDataValidator()
    client = Client()

    def test_submit_fails_when_url_and_file_are_empty(self):
        data_dict = {}
        with self.assertRaises(ValidationError):
            self.validator.get_and_validate_data(data_dict)

    def test_submit_fails_when_both_url_and_file_have_content(self):
        data_dict = {'file': "something", 'url': 'string'}
        with self.assertRaises(ValidationError):
            self.validator.get_and_validate_data(data_dict)

    @requests_mock.mock()
    def test_fails_when_response_is_not_successful(self, mock):
        mock.get('https://fake_url.com/data.json', text="Testing text", status_code=404)
        data_dict = {'format': 'json', 'identifier': 'test',
                     'url': 'https://fake_url.com/data.json'}
        with self.assertRaises(HTTPError):
            self.validator.get_and_validate_data(data_dict)

    @requests_mock.mock()
    def test_returns_correct_data_when_specifying_url(self, mock):
        mock.get('https://fake_url.com/data.json', text="Testing text")
        data_dict = {'format': 'json', 'identifier': 'test',
                     'url': 'https://fake_url.com/data.json'}
        data = self.validator.get_and_validate_data(data_dict)
        assert data['file'].read() == b"Testing text"

    def test_returns_correct_data_when_uploading_file(self):
        with open('infra/apps/catalog/tests/samples/simple.json', 'r+') as local_file:
            data_dict = {'format': 'json', 'identifier': 'test', 'file': local_file}
            data = self.validator.get_and_validate_data(data_dict)
            assert data['file'].read() == '{"identifier": "test"}'

    def test_catalogs_page_renders_catalogs_index_template(self):
        response = self.client.get('/catalogs/')
        response_templates_names = [template.name for template in response.templates]
        self.assertIn('index.html', response_templates_names)

    def test_form_submit_with_valid_data_redirects_to_catalogs_index(self):
        with open('infra/apps/catalog/tests/samples/simple.json', 'r+') as local_file:
            form_data = {'format': 'json', 'identifier': 'test', 'file': local_file}
            response = self.client.post('/catalogs/add', form_data, follow=True)
            self.assertEqual(response.redirect_chain[-1], ('/catalogs/', 302))

            response_templates_names = [template.name for template in response.templates]
            self.assertIn('index.html', response_templates_names)

    def test_catalog_is_created_when_submitted_form_is_valid(self):
        with open('infra/apps/catalog/tests/samples/simple.json', 'r+') as local_file:
            form_data = {'format': 'json', 'identifier': 'test', 'file': local_file}
            self.client.post('/catalogs/add', form_data)
            self.assertEqual(1, Catalog.objects.count())
