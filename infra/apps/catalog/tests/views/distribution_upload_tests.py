import pytest
from django.core.files import File
from django.urls import reverse
from freezegun import freeze_time

from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


def _call(client, distribution):
    return client.get(reverse('catalog:distribution_uploads',
                              kwargs={'node_id': distribution.node.id,
                                      'identifier': distribution.identifier}))


def test_file_name_listed(client, distribution):
    response = _call(client, distribution)
    assert distribution.file_name in response.content.decode('utf-8')


def test_older_versions_listed(client, distribution):
    with freeze_time('2019-01-01'):
        with open_catalog('test_data.csv') as fd:
            other = distribution.node.distribution_set \
                .create(file=File(fd),
                        identifier=distribution.identifier,
                        dataset_identifier=distribution.dataset_identifier)

    response = _call(client, distribution)
    assert str(other.uploaded_at) in response.content.decode('utf-8')


def test_catalog_identifier_in_page(client, distribution):
    response = _call(client, distribution)
    assert distribution.node.identifier in response.content.decode('utf-8')
