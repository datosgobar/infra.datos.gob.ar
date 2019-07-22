# coding=utf-8
import requests_mock
from django.test import TestCase, Client
from django.urls import reverse

from infra.apps.catalog.models import CatalogUpload
from infra.apps.catalog.tests.conftest import _node
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog


class TestCatalogViews(TestCase):
    client = Client()

    def setUp(self) -> None:
        self.node = _node()

    def test_catalogs_page_renders_catalogs_index_template(self):
        response = self.client.get(reverse('catalog:list'))
        response_templates_names = [template.name for template in response.templates]
        self.assertIn('index.html', response_templates_names)

    def test_form_submit_with_valid_data_redirects_to_catalogs_index(self):
        with open_catalog('valid_data.json') as sample:
            form_data = {'format': 'json', 'node': self.node.id, 'file': sample}
            response = self.client.post(reverse('catalog:add'), form_data)
            self.assertEqual(response.status_code, 302)

            self.assertEqual(response.url, reverse('catalog:list'))

    def test_catalog_is_created_when_submitted_form_is_valid(self):
        with open_catalog('valid_data.json') as sample:
            form_data = {'format': 'json', 'node': self.node.id, 'file': sample}
            self.client.post(reverse('catalog:add'), form_data)
            self.assertEqual(1, CatalogUpload.objects.count())

    @requests_mock.mock()
    def test_returns_400_if_catalog_url_not_found(self, mock):
        mock.get('https://fakeurl.com/data.json', text="Testing text", status_code=404)
        data_dict = {'format': 'json', 'node': self.node,
                     'url': 'https://fakeurl.com/data.json'}
        response = self.client.post(reverse('catalog:add'), data_dict, follow=True)
        self.assertEqual(response.status_code, 400)
