import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_get(client, catalog):
    response = client.get(_url(catalog.node))
    assert response.status_code == 200


def test_get_404_when_node_does_not_exist(client):
    response = client.get(reverse('catalog:add_distribution', kwargs={'node': 1}))
    assert response.status_code == 404


def test_get_400_when_node_has_no_catalog_uploaded(client, node):
    response = client.get(_url(node))
    assert response.status_code == 400


def test_post_invalid_data(client, catalog):
    form_data = {}

    response = client.post(_url(catalog.node), form_data)
    assert response.status_code == 400


def test_post_both_url_and_file(client, catalog):
    form_data = {'url': 'https://fakeurl.com/data.csv', 'file': ''}

    response = client.post(_url(catalog.node), form_data)
    assert response.status_code == 400


def _url(node):
    return reverse('catalog:add_distribution', kwargs={'node': node.id})
