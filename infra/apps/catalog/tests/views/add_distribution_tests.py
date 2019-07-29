from io import BytesIO

import pytest
from django.urls import reverse

from infra.apps.catalog.models import Distribution
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


def test_get(admin_client, catalog):
    response = admin_client.get(_url(catalog.node))
    assert response.status_code == 200


def test_get_404_when_node_does_not_exist(admin_client):
    response = admin_client.get(reverse('catalog:add_distribution', kwargs={'node_id': 1}))
    assert response.status_code == 404


def test_get_400_when_node_has_no_catalog_uploaded(admin_client, node):
    response = admin_client.get(_url(node))
    assert response.status_code == 400


def test_post_invalid_data(admin_client, catalog):
    form_data = {}

    response = admin_client.post(_url(catalog.node), form_data)
    assert response.status_code == 400


def test_post_both_url_and_file(admin_client, catalog, requests_mock):
    url = 'https://fakeurl.com/data.csv'
    requests_mock.get(url,
                      text='test_content')

    form_data = {'url': 'https://fakeurl.com/data.csv', 'file': BytesIO(b'some_file_content'),
                 'dataset_identifier': "125", 'distribution_identifier': "125.1"}

    response = admin_client.post(_url(catalog.node), form_data)
    assert response.status_code == 400


def test_create_from_url(admin_client, catalog, requests_mock):
    url = 'https://fakeurl.com/data.csv'
    requests_mock.get(url,
                      text='test_content')

    form_data = {'url': url,
                 'dataset_identifier': "125", 'distribution_identifier': "125.1"}

    admin_client.post(_url(catalog.node), form_data)
    assert Distribution.objects.get().identifier == "125.1"


def test_create_from_url_404(admin_client, catalog, requests_mock):
    url = 'https://fakeurl.com/data.csv'
    requests_mock.get(url,
                      status_code=404)

    form_data = {'url': url,
                 'dataset_identifier': "125", 'distribution_identifier': "125.1"}

    response = admin_client.post(_url(catalog.node), form_data)
    assert response.status_code == 400


def test_create_from_file(admin_client, catalog):
    with open_catalog('test_data.csv') as sample:
        form_data = {'file': sample,
                     'dataset_identifier': "125", 'distribution_identifier': "125.1"}

        admin_client.post(_url(catalog.node), form_data)
    assert Distribution.objects.get().identifier == "125.1"


def _url(node):
    return reverse('catalog:add_distribution', kwargs={'node_id': node.id})
