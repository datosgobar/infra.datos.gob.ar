import datetime

import pytest
from django.core.files import File
from django.urls import reverse

from infra.apps.catalog.models import Node, DistributionUpload, Distribution
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog


@pytest.fixture(autouse=True)
def give_user_edit_rights(user, node):
    node.admins.add(user)


def test_delete_dist_upload_admin(logged_client, distribution_upload):
    node = distribution_upload.distribution.catalog
    node.admins.clear()
    response = logged_client.post(reverse('catalog:delete_distribution_upload',
                                          kwargs={
                                              'node_id': node.id,
                                              'pk': distribution_upload.pk
                                          }))

    assert response.status_code == 403


def test_delete_dist_upload_invalid_node_id(logged_client, distribution_upload):
    node = distribution_upload.distribution.catalog
    response = logged_client.post(reverse('catalog:delete_distribution_upload',
                                          kwargs={
                                              'node_id': node.id + 1,
                                              'pk': distribution_upload.pk
                                          }))

    assert response.status_code == 403


def test_delete_dist_upload_of_another_node(user, logged_client, distribution_upload):
    node2 = Node.objects.get_or_create(identifier="Test Node 2")[0]
    node2.admins.add(user)
    distribution_upload.distribution.catalog.admins.clear()
    response = logged_client.post(reverse('catalog:delete_distribution_upload',
                                          kwargs={
                                              'node_id': node2.id,
                                              'pk': distribution_upload.pk
                                          }))

    assert response.status_code == 401


def test_delete_dist_upload_invalid_catalog_pk(logged_client, distribution_upload):
    node = distribution_upload.distribution.catalog
    response = logged_client.post(reverse('catalog:delete_distribution_upload',
                                          kwargs={
                                              'node_id': node.id,
                                              'pk': distribution_upload.pk + 1
                                          }))

    assert response.status_code == 404


def test_delete_valid_dist_upload(logged_client, distribution_upload):
    distribution = distribution_upload.distribution
    node = distribution.catalog
    logged_client.post(reverse('catalog:delete_distribution_upload',
                               kwargs={
                                   'node_id': node.id,
                                   'pk': distribution_upload.pk
                               }))

    assert distribution.distributionupload_set.count() == 0


def test_delete_the_unique_version_deletes_the_distribution_too(logged_client, distribution_upload):
    distribution = distribution_upload.distribution
    node = distribution.catalog
    logged_client.post(reverse('catalog:delete_distribution_upload',
                               kwargs={
                                   'node_id': node.id,
                                   'pk': distribution_upload.pk
                               }))

    assert not Distribution.objects.filter(pk=distribution.pk).count()


def test_delete_not_the_unique_version_not_deletes_the_distribution(logged_client, distribution_upload):
    distribution = distribution_upload.distribution
    node = distribution.catalog
    _create_dist2(distribution, distribution_upload)
    logged_client.post(reverse('catalog:delete_distribution_upload',
                               kwargs={
                                   'node_id': node.id,
                                   'pk': distribution_upload.pk
                               }))

    assert Distribution.objects.filter(pk=distribution.pk).count()


def test_delete_the_unique_version_redirects_to_distribution_list(logged_client, distribution_upload):
    distribution = distribution_upload.distribution
    node = distribution.catalog
    response = logged_client.post(reverse('catalog:delete_distribution_upload',
                                  kwargs={
                                      'node_id': node.id,
                                      'pk': distribution_upload.pk
                                  }))

    assert response.url == reverse('catalog:node_distributions', kwargs={'node_id': node.id})


def test_delete_not_the_unique_version_redirect_to_distribution_history(logged_client, distribution_upload):

    node = distribution_upload.distribution.catalog
    distribution = distribution_upload.distribution
    _create_dist2(distribution, distribution_upload)
    response = logged_client.post(reverse('catalog:delete_distribution_upload',
                                          kwargs={
                                              'node_id': node.id,
                                              'pk': distribution_upload.pk
                                          }))

    assert response.url == reverse('catalog:distribution_uploads',
                                   kwargs={
                                       'node_id': node.id,
                                       'identifier': distribution.identifier
                                   })


def test_get_method_not_supported(logged_client, distribution_upload):
    node = distribution_upload.distribution.catalog
    resp = logged_client.get(reverse('catalog:delete_distribution_upload',
                                     kwargs={
                                         'node_id': node.id,
                                         'pk': distribution_upload.pk
                                     }))

    assert resp.status_code == 405


def _create_dist2(distribution, distribution_upload):
    last_week = datetime.datetime.now() - datetime.timedelta(days=7)
    DistributionUpload.objects.filter(pk=distribution_upload.pk).update(uploaded_at=last_week)
    with open_catalog('test_data.csv') as distribution_fd:
        dist2 = distribution.distributionupload_set.create(file=File(distribution_fd))
        dist2.save()
    return dist2
