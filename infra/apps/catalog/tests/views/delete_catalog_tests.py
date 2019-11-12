import pytest
from django.urls import reverse

from infra.apps.catalog.models import Node


@pytest.fixture(autouse=True)
def give_user_edit_rights(user, node):
    node.admins.add(user)


def test_delete_catalog_admin(logged_client, catalog):
    node = catalog.node
    node.admins.clear()
    response = logged_client.post(reverse('catalog:delete_catalog_upload',
                                          kwargs={
                                              'node_id': node.id,
                                              'pk': catalog.pk
                                          }))

    assert response.status_code == 403


def test_delete_catalog_invalid_node_id(logged_client, catalog):

    response = logged_client.post(reverse('catalog:delete_catalog_upload',
                                          kwargs={
                                              'node_id': catalog.node.id + 1,
                                              'pk': catalog.pk
                                          }))

    assert response.status_code == 403


def test_delete_catalog_of_another_node(user, logged_client, catalog):
    node2 = Node.objects.get_or_create(identifier="Test Node 2")[0]
    node2.admins.add(user)
    catalog.node.admins.clear()
    response = logged_client.post(reverse('catalog:delete_catalog_upload',
                                  kwargs={
                                      'node_id': node2.id,
                                      'pk': catalog.pk
                                  }))

    assert response.status_code == 401


def test_delete_catalog_invalid_catalog_pk(logged_client, catalog):
    node = catalog.node
    response = logged_client.post(reverse('catalog:delete_catalog_upload',
                                          kwargs={
                                              'node_id': node.id,
                                              'pk': catalog.pk + 1
                                          }))

    assert response.status_code == 404


def test_delete_valid_catalog(logged_client, catalog):
    node = catalog.node
    logged_client.post(reverse('catalog:delete_catalog_upload',
                               kwargs={
                                   'node_id': node.id,
                                   'pk': catalog.pk
                               }))

    assert node.catalogupload_set.count() == 0


def test_get_method_not_supported(logged_client, catalog):
    node = catalog.node
    resp = logged_client.get(reverse('catalog:delete_catalog_upload',
                                     kwargs={
                                         'node_id': node.id,
                                         'pk': catalog.pk
                                     }))

    assert resp.status_code == 405
