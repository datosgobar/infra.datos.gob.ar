import pytest
from django.core.files import File

from infra.apps.catalog.exceptions.catalog_not_uploaded_error import CatalogNotUploadedError
from infra.apps.catalog.models.distribution import Distribution
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


def test_upload_distribution_contains_distribution_id(catalog):
    with open_catalog('test_data.csv') as distribution:
        Distribution.objects.create(node=catalog.node,
                                    dataset_identifier='125',
                                    identifier='125.1',
                                    file=File(distribution))

    assert '125.1' in Distribution.objects.first().file.name


def test_upload_distribution_to_node_without_catalogs_uploaded_fails(node):
    with open_catalog('test_data.csv') as distribution:
        with pytest.raises(CatalogNotUploadedError):
            Distribution.objects.create(node=node,
                                        dataset_identifier='125',
                                        identifier='125.1',
                                        file=File(distribution))


def test_read_from_url(catalog, requests_mock):
    url = 'https://fakeurl.com/data.csv'
    requests_mock.get(url,
                      text='test_content')

    distribution = Distribution.create_from_url(url, catalog.node, "125", "125.1")
    assert distribution.file.read() == b'test_content'
