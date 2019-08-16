# coding=utf-8
import requests_mock
from django.test import TestCase, Client
from django.urls import reverse

from infra.apps.catalog.models import CatalogUpload
from infra.apps.catalog.tests.conftest import _node, _user
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog


class TestCatalogViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = _user()
        cls.client = Client()

    def setUp(self) -> None:
        self.node = _node()
        self.node.admins.add(self.user)
        self.node.save()
        self.client.login(username='user', password='password')

    def test_form_submit_with_valid_data_redirects_to_success_page(self):
        with open_catalog('valid_data.json') as sample:
            form_data = {'format': 'json', 'node': self.node.identifier, 'file': sample}
            response = self.client.post(
                reverse('catalog:add_catalog', kwargs={'node_id': self.node.id}),
                form_data)
            self.assertEqual(response.status_code, 302)

            self.assertEqual(response.url,
                             reverse('catalog:upload_success', kwargs={'node_id': self.node.id}))

    def test_catalog_is_created_when_submitted_form_is_valid(self):
        with open_catalog('valid_data.json') as sample:
            form_data = {'format': 'json',
                         'node': self.node.identifier,
                         'file': sample}
            self.client.post(
                reverse('catalog:add_catalog', kwargs={'node_id': self.node.id}),
                form_data)
            self.assertEqual(1, CatalogUpload.objects.count())

    @requests_mock.mock()
    def test_returns_400_if_catalog_url_not_found(self, mock):
        mock.get('https://fakeurl.com/data.json', text="Testing text", status_code=404)
        data_dict = {'format': 'json', 'node': self.node.identifier,
                     'url': 'https://fakeurl.com/data.json'}
        response = self.client.post(
            reverse('catalog:add_catalog', kwargs={'node_id': self.node.id}),
            data_dict,
            follow=True)
        self.assertEqual(response.status_code, 400)

    def test_redirects_even_if_catalog_is_not_valid(self):
        with open_catalog('data.json') as sample:
            form_data = {'format': 'json', 'node': self.node.identifier, 'file': sample}
            response = self.client.post(
                reverse('catalog:add_catalog', kwargs={'node_id': self.node.id}),
                form_data)
            self.assertEqual(response.status_code, 302)

    def test_error_messages_in_view_if_catalog_is_not_valid(self):
        with open_catalog('data.json') as sample:
            form_data = {'format': 'json', 'node_id': self.node.id, 'file': sample}
            response = self.client.post(
                reverse('catalog:add_catalog', kwargs={'node_id': self.node.id}),
                form_data,
                follow=True)
            self.assertIsNotNone(response.context['messages'])

    def test_view_messages_includes_error_messages_from_validator(self):
        error_messages = [
            "'title' is a required property",
            "'description' is a required property",
            "'publisher' is a required property",
            "'superThemeTaxonomy' is a required property",
            "'Índice-precios-internos-basicos-al-por-mayor-desagregado-base-1993-anual.csv' "
            "is not valid under any of the given schemas",
        ]
        with open_catalog('data.json') as sample:
            form_data = {'format': 'json', 'node': self.node.identifier, 'file': sample}
            response = self.client.post(
                reverse('catalog:add_catalog', kwargs={'node_id': self.node.id}),
                form_data,
                follow=True)

            messages = [str(message) for message in list(response.context['messages'])]
            self.assertCountEqual(error_messages, messages)
