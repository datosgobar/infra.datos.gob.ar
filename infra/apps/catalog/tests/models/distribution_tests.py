import os

import pytest
from django.conf import settings
from django.core.files import File

from infra.apps.catalog.exceptions.catalog_not_uploaded_error import CatalogNotUploadedError
from infra.apps.catalog.models.distribution import Distribution
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


def test_upload_distribution_contains_distribution_id(catalog):
    with open_catalog('test_data.csv') as distribution:
        Distribution.objects.create(node=catalog.node,
                                    dataset_identifier='125',
                                    file_name='test_data.csv',
                                    identifier='125.1',
                                    file=File(distribution))

    assert '125.1' in Distribution.objects.first().file.name


def test_upload_distribution_to_node_without_catalogs_uploaded_fails(node):
    with open_catalog('test_data.csv') as distribution:
        with pytest.raises(CatalogNotUploadedError):
            Distribution.objects.create(node=node,
                                        dataset_identifier='125',
                                        file_name='test_data.csv',
                                        identifier='125.1',
                                        file=File(distribution))


def test_read_from_url(catalog, requests_mock):
    url = 'https://fakeurl.com/data.csv'
    requests_mock.get(url,
                      text='test_content')

    raw_data = {'dataset_identifier': '125',
                'file_name': 'data.csv',
                'identifier': "125.1",
                'node': catalog.node,
                'url': url}
    distribution = Distribution.create_from_url(raw_data)
    assert distribution.file.read() == b'test_content'


def test_file_upload_large_name(catalog):
    long_name = 'extremely_long_distribution_id_that_makes_final_name_very_big'
    with open_catalog('test_data.csv') as distribution:
        Distribution.objects.create(node=catalog.node,
                                    dataset_identifier='125',
                                    file_name='test_data.csv',
                                    identifier=long_name,
                                    file=File(distribution))

    assert Distribution.objects.count() == 1


def test_file_saved_as_latest(catalog):
    with open_catalog('test_data.csv') as distribution:
        distribution = Distribution.objects.create(node=catalog.node,
                                                   dataset_identifier='125',
                                                   file_name='test_data.csv',
                                                   identifier='125.1',
                                                   file=File(distribution))

    assert os.path.exists(os.path.join(settings.MEDIA_ROOT,
                                       'catalog',
                                       catalog.node.identifier,
                                       'dataset',
                                       '125',
                                       'distribution',
                                       '125.1',
                                       'download',
                                       distribution.file_name))
