# coding=utf-8
from django.test import TestCase, Client

from infra.apps.catalog.models import Catalog


class TestCatalogViews(TestCase):
    client = Client()

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
