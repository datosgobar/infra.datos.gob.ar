import pytest
from django.core.files import File
from django.urls import reverse
from freezegun import freeze_time

from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def give_user_edit_rights(user, node):
    node.admins.add(user)


def _call(client, distribution):
    return client.get(reverse('catalog:distribution_uploads',
                              kwargs={'node_id': distribution.catalog.id,
                                      'identifier': distribution.identifier}))


def test_older_versions_listed(logged_client, distribution_upload):
    distribution = distribution_upload.distribution
    with freeze_time('2019-01-01'):
        with open_catalog('test_data.csv') as fd:
            other = distribution.distributionupload_set \
                .create(file=File(fd))
    response = _call(logged_client, distribution)
    assert str(other.uploaded_at) in response.content.decode('utf-8')


def test_catalog_identifier_in_page(logged_client, distribution):
    response = _call(logged_client, distribution)
    assert distribution.catalog.identifier in response.content.decode('utf-8')
