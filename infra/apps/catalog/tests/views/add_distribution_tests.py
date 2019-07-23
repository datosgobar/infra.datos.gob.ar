import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_get(client, catalog):
    response = client.get(reverse('catalog:add_distribution', kwargs={'node': catalog.node.id}))
    assert response.status_code == 200


def test_get_404_when_node_does_not_exist(client):
    response = client.get(reverse('catalog:add_distribution', kwargs={'node': 1}))
    assert response.status_code == 404


def test_get_400_when_node_has_no_catalog_uploaded(client, node):
    response = client.get(reverse('catalog:add_distribution', kwargs={'node': node.id}))
    assert response.status_code == 400
