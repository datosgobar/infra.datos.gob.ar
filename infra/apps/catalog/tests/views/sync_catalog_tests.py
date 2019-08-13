from shutil import copy2

from django.urls import reverse

from infra.apps.catalog.tests.helpers.open_catalog import catalog_path


def test_sync_catalog_not_superuser(logged_client, node):

    response = logged_client.post(reverse('catalog:sync_catalog', kwargs={'node_id': node.id}))

    assert response.status_code == 403


def test_sync_catalog_invalid_id(admin_client):

    response = admin_client.post(reverse('catalog:sync_catalog', kwargs={'node_id': '1'}))

    assert response.status_code == 400


def test_invalid_catalog_in_file_system(admin_client, node, catalog_dest):
    copy2(catalog_path('catalogo-justicia.xlsx'), catalog_dest)
    response = admin_client.post(reverse('catalog:sync_catalog', kwargs={'node_id': node.id}))
    assert response.status_code == 400


def test_sync_catalog_not_found(admin_client, node):
    response = admin_client.post(reverse('catalog:sync_catalog', kwargs={'node_id': node.id}))
    assert response.status_code == 400


def test_sync_valid_catalog(admin_client, node, catalog_dest):
    copy2(catalog_path('data.json'), catalog_dest)
    admin_client.post(reverse('catalog:sync_catalog', kwargs={'node_id': node.id}))
    assert node.catalogupload_set.count() == 1
