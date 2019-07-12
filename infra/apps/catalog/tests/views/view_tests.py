# coding=utf-8
import requests_mock
from django.test import TestCase, Client

from infra.apps.catalog.models import Catalog
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog


class TestCatalogViews(TestCase):
    client = Client()

    def test_catalogs_page_renders_catalogs_index_template(self):
        response = self.client.get('/catalogs/')
        response_templates_names = [template.name for template in response.templates]
        self.assertIn('index.html', response_templates_names)

    def test_form_submit_with_valid_data_redirects_to_catalogs_index(self):
        with open_catalog('simple.json') as sample:
            form_data = {'format': 'json', 'identifier': 'test', 'file': sample}
            response = self.client.post('/catalogs/add/', form_data, follow=True)
            self.assertEqual(response.redirect_chain[-1], ('/catalogs/', 302))

            response_templates_names = [template.name for template in response.templates]
            self.assertIn('index.html', response_templates_names)

    def test_catalog_is_created_when_submitted_form_is_valid(self):
        with open_catalog('simple.json') as sample:
            form_data = {'format': 'json', 'identifier': 'test', 'file': sample}
            self.client.post('/catalogs/add/', form_data)
            self.assertEqual(1, Catalog.objects.count())

    @requests_mock.mock()
    def test_returns_400_if_catalog_url_not_found(self, mock):
        mock.get('https://fakeurl.com/data.json', text="Testing text", status_code=404)
        data_dict = {'format': 'json', 'identifier': 'test',
                     'url': 'https://fakeurl.com/data.json'}
        response = self.client.post('/catalogs/add/', data_dict, follow=True)
        self.assertEqual(response.status_code, 400)