from io import BytesIO
from os.path import isfile, join

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from infra.apps.catalog.models import DistributionUpload
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


def test_get(admin_client, catalog):
    response = admin_client.get(_add_url(catalog.node))
    assert response.status_code == 200


def test_get_404_when_node_does_not_exist(admin_client):
    response = admin_client.get(reverse('catalog:add_distribution', kwargs={'node_id': 1}))
    assert response.status_code == 404


def test_get_400_when_node_has_no_catalog_uploaded(admin_client, node):
    response = admin_client.get(_add_url(node))
    assert response.status_code == 400


def test_post_invalid_data(admin_client, catalog):
    form_data = {}

    response = admin_client.post(_add_url(catalog.node), form_data)
    assert response.status_code == 400


def test_post_with_neither_url_nor_file(admin_client, catalog):
    form_data = {'dataset_identifier': "125", 'distribution_identifier': "125.1"}

    response = admin_client.post(_add_url(catalog.node), form_data)
    assert response.status_code == 400


def test_post_both_url_and_file(admin_client, catalog, requests_mock):
    url = 'https://fakeurl.com/data.csv'
    requests_mock.get(url,
                      text='test_content')

    form_data = {'url': 'https://fakeurl.com/data.csv', 'file': BytesIO(b'some_file_content'),
                 'dataset_identifier': "125", 'distribution_identifier': "125.1"}

    response = admin_client.post(_add_url(catalog.node), form_data)
    assert response.status_code == 400


def test_create_from_url(admin_client, catalog, requests_mock):
    url = 'https://fakeurl.com/data.csv'
    requests_mock.get(url,
                      text='test_content')

    form_data = {'url': url,
                 'dataset_identifier': "125",
                 'distribution_identifier': "125.1",
                 'file_name': "data.csv"}

    admin_client.post(_add_url(catalog.node), form_data)
    assert DistributionUpload.objects.get().distribution.identifier == "125.1"


def test_create_from_url_404(admin_client, catalog, requests_mock):
    url = 'https://fakeurl.com/data.csv'
    requests_mock.get(url,
                      status_code=404)

    form_data = {'url': url,
                 'dataset_identifier': "125", 'distribution_identifier': "125.1"}

    response = admin_client.post(_add_url(catalog.node), form_data)
    assert response.status_code == 400


def test_create_from_file(admin_client, catalog):
    with open_catalog('test_data.csv') as sample:
        form_data = {'file': sample,
                     'dataset_identifier': "125",
                     'distribution_identifier': "125.1",
                     'file_name': 'test_data.csv'}

        admin_client.post(_add_url(catalog.node), form_data)
    assert DistributionUpload.objects.get().distribution.identifier == "125.1"


def test_posting_new_version_twice_persists_only_one_instance(client, catalog):
    with open_catalog('test_data.csv') as sample:
        form_data = {'file': sample,
                     'dataset_identifier': "125",
                     'distribution_identifier': "125.1",
                     'file_name': 'test_data.csv'}

        client.post(_add_url(catalog.node), form_data)

        sample.seek(0)
        client.post(_add_version_url(catalog.node, form_data['distribution_identifier']), form_data)
    assert DistributionUpload.objects.count() == 1


def test_context_manager_does_not_lose_files_using_same_file_name(client, distribution_upload):
    file_path = join('tests_media', distribution_upload.file_path())
    file_path_with_date = join('tests_media', distribution_upload.file_path(with_date=True))
    with open_catalog('test_data.csv') as sample:
        raw_data = {'node': distribution_upload.distribution.catalog,
                    'dataset_identifier': distribution_upload.distribution.dataset_identifier,
                    'distribution_identifier': distribution_upload.distribution.identifier,
                    'file_name': distribution_upload.distribution.file_name,
                    'file': sample}
        client.post(_add_url(distribution_upload.distribution.catalog), raw_data)
    assert isfile(file_path) and isfile(file_path_with_date)


def test_context_manager_removes_old_same_day_version_file_if_name_changes(client,
                                                                           distribution_upload):
    old_file_path = join('tests_media', distribution_upload.file_path())
    with open_catalog('test_data.csv') as sample:
        raw_data = {'node': distribution_upload.distribution.catalog,
                    'dataset_identifier': distribution_upload.distribution.dataset_identifier,
                    'distribution_identifier': distribution_upload.distribution.identifier,
                    'file_name': 'new_file_name.csv',
                    'file': sample}
        client.post(_add_url(distribution_upload.distribution.catalog), raw_data)
    updated_distribution = DistributionUpload.objects \
        .get(distribution=distribution_upload.distribution)
    new_file_path = join(settings.MEDIA_ROOT, updated_distribution.file_path())
    assert new_file_path != old_file_path
    assert not isfile(old_file_path)
    assert isfile(new_file_path)


def test_new_version_form_contains_previous_data(client, catalog):
    with open_catalog('test_data.csv') as sample:
        form_data = {'file': sample,
                     'dataset_identifier': "125",
                     'distribution_identifier': "an_easily_findable_distribution_identifier",
                     'file_name': 'an_easily_findable_file_name.csv'}

        client.post(_add_url(catalog.node), form_data)

        sample.seek(0)
        response = client.get(_add_version_url(catalog.node, form_data['distribution_identifier']))
    response_content = response.content.decode('utf-8')
    assert "125" in response_content
    assert "an_easily_findable_distribution_identifier" in response_content
    assert "an_easily_findable_file_name.csv" in response_content


def test_generated_file_paths_for_distribution(admin_client, catalog):
    with open_catalog('test_data.csv') as sample:
        form_data = {'file': sample,
                     'dataset_identifier': "125",
                     'distribution_identifier': "125.1",
                     'file_name': 'test_data.csv'}

        admin_client.post(_add_url(catalog.node), form_data)
    distribution = DistributionUpload.objects.get()
    assert str(distribution.file_path()) == 'catalog/test_id/dataset/125/distribution/125.1/' \
                                            'download/test_data.csv'
    assert str(distribution.file_path(with_date=True)) == f'catalog/test_id/dataset/125/' \
                                                          f'distribution/125.1/download/test_data' \
                                                          f'-{timezone.now().date()}.csv'


def _add_url(node):
    return reverse('catalog:add_distribution', kwargs={'node_id': node.id})


def _add_version_url(node, identifier):
    return reverse('catalog:add_distribution_version',
                   kwargs={'node_id': node.id, 'identifier': identifier})
