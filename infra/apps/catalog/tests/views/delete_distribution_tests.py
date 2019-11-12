import os

from django.conf import settings
from django.urls import reverse

from infra.apps.catalog.models import Distribution


def test_delete_distribution(logged_client, distribution):
    logged_client.post(reverse('catalog:delete_distribution',
                               kwargs={'node_id': distribution.catalog.id,
                                       'identifier': distribution.identifier}))

    # Ya no hay mas subidas
    assert Distribution.objects.count() == 0


def test_if_uploads_existed_they_are_deleted(logged_client, distribution_upload):
    distribution = distribution_upload.distribution
    logged_client.post(reverse('catalog:delete_distribution',
                               kwargs={'node_id': distribution.catalog.id,
                                       'identifier': distribution.identifier}))

    filepath = os.path.join(settings.MEDIA_ROOT, distribution_upload.file_path())
    assert not os.path.isfile(filepath)


def test_node_does_not_exist(logged_client, distribution):
    resp = logged_client.post(reverse('catalog:delete_distribution',
                                      kwargs={'node_id': 20,
                                              'identifier': distribution.identifier}))

    assert resp.status_code == 400


def test_distribution_does_not_exist(logged_client, node):
    resp = logged_client.post(reverse('catalog:delete_distribution',
                                      kwargs={'node_id': node.id,
                                              'identifier': 'bad_id'}))

    assert resp.status_code == 400


def test_get_method_not_supported(logged_client, node):
    resp = logged_client.get(reverse('catalog:delete_distribution',
                                     kwargs={'node_id': node.id,
                                             'identifier': 'bad_id'}))

    assert resp.status_code == 405


def test_delete_distribution_of_unauthorized_node(logged_client, node, distribution_upload):
    distribution = distribution_upload.distribution
    node.admins.clear()

    resp = logged_client.post(reverse('catalog:delete_distribution',
                                      kwargs={'node_id': distribution.catalog.id,
                                              'identifier': distribution.identifier}))

    assert resp.status_code == 403
