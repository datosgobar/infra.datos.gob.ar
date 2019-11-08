import os
from pathlib import Path

import pytest
from django.conf import settings
from django.core.files import File
from freezegun import freeze_time

from infra.apps.catalog.exceptions.catalog_not_uploaded_error import CatalogNotUploadedError
from infra.apps.catalog.models.distribution import DistributionUpload, Distribution
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


def test_upload_distribution_contains_distribution_id(distribution):
    with open_catalog('test_data.csv') as f:
        distribution.distributionupload_set.create(file=File(f))

    assert '125.1' in DistributionUpload.objects.first().file.name


def test_upload_distribution_to_node_without_catalogs_uploaded_fails(node):
    with pytest.raises(CatalogNotUploadedError):
        Distribution.objects.create(catalog=node,
                                    dataset_identifier='125',
                                    file_name='test_data.csv',
                                    identifier='125.1')


def test_read_from_url(catalog, requests_mock):
    url = 'https://fakeurl.com/data.csv'
    requests_mock.get(url,
                      text='test_content')

    raw_data = {'dataset_identifier': '125',
                'file_name': 'data.csv',
                'distribution_identifier': "125.1",
                'node': catalog.node,
                'url': url}
    distribution = Distribution.objects.upsert_upload(catalog.node, raw_data)
    assert distribution.file.read() == b'test_content'


def test_file_upload_large_name(distribution):
    long_name = 'extremely_long_distribution_id_that_makes_final_name_very_big'
    distribution.identifier = long_name
    distribution.save()
    with open_catalog('test_data.csv') as f:
        distribution.distributionupload_set.create(file=File(f))

    assert DistributionUpload.objects.count() == 1


def test_file_saved_as_latest(distribution):
    with open_catalog('test_data.csv') as f:
        distribution.distributionupload_set.create(file=File(f))

    assert os.path.exists(os.path.join(settings.MEDIA_ROOT,
                                       'catalog',
                                       distribution.catalog.identifier,
                                       'dataset',
                                       '125',
                                       'distribution',
                                       '125.1',
                                       'download',
                                       distribution.file_name))


def test_upload_distribution_filename_with_extension(distribution):
    distribution.file_name = 'file_with_extension.csv'
    with freeze_time('2019-01-01'):
        with open_catalog('test_data.csv') as f:
            distribution.distributionupload_set.create(file=File(f))
        dist_filename = Path(DistributionUpload.objects.first().file.name).name
    assert dist_filename == 'file_with_extension-2019-01-01.csv'


def test_upload_distribution_filename_without_extension(distribution):
    distribution.file_name = 'file_without_extension'
    with freeze_time('2019-01-01'):
        with open_catalog('test_data.csv') as f:
            distribution.distributionupload_set.create(file=File(f))
        dist_filename = Path(DistributionUpload.objects.first().file.name).name
    assert dist_filename == 'file_without_extension-2019-01-01'
