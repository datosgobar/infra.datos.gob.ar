from io import BytesIO

import pytest
from django.urls import reverse

from infra.apps.catalog.models import Distribution
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


def test_get(client, catalog):
    response = client.get(_url(catalog.node))
    assert response.status_code == 200


def test_get_404_when_node_does_not_exist(client):
    response = client.get(reverse('catalog:add_distribution', kwargs={'node_id': 1}))
    assert response.status_code == 404


def test_get_400_when_node_has_no_catalog_uploaded(client, node):
    response = client.get(_url(node))
    assert response.status_code == 400


def test_post_invalid_data(client, catalog):
    form_data = {}

    response = client.post(_url(catalog.node), form_data)
    assert response.status_code == 400


def test_post_both_url_and_file(client, catalog, requests_mock):
    url = 'https://fakeurl.com/data.csv'
    requests_mock.get(url,
                      text='test_content')

    form_data = {'url': 'https://fakeurl.com/data.csv', 'file': BytesIO(b'some_file_content'),
                 'dataset_identifier': "125", 'distribution_identifier': "125.1"}

    response = client.post(_url(catalog.node), form_data)
    assert response.status_code == 400


def test_create_from_url(client, catalog, requests_mock):
    url = 'https://fakeurl.com/data.csv'
    requests_mock.get(url,
                      text='test_content')

    form_data = {'url': url,
                 'dataset_identifier': "125", 'distribution_identifier': "125.1"}

    client.post(_url(catalog.node), form_data)
    assert Distribution.objects.get().identifier == "125.1"


def test_create_from_url_404(client, catalog, requests_mock):
    url = 'https://fakeurl.com/data.csv'
    requests_mock.get(url,
                      status_code=404)

    form_data = {'url': url,
                 'dataset_identifier': "125", 'distribution_identifier': "125.1"}

    response = client.post(_url(catalog.node), form_data)
    assert response.status_code == 400


def test_create_from_file(client, catalog):
    with open_catalog('test_data.csv') as sample:
        form_data = {'file': sample,
                     'dataset_identifier': "125", 'distribution_identifier': "125.1"}

        client.post(_url(catalog.node), form_data)
    assert Distribution.objects.get().identifier == "125.1"


def _url(node):
    return reverse('catalog:add_distribution', kwargs={'node_id': node.id})
