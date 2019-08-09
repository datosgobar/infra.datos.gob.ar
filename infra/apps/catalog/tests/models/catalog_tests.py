import os
import stat

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import IntegrityError
from django.utils import timezone

from infra.apps.catalog.models import CatalogUpload
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


def test_catalog_saves_to_identifier_path(catalog):
    path = f'catalog/{catalog.node.identifier}/data'
    assert path in CatalogUpload.objects.first().file.name


def test_catalog_format_saved_in_file(catalog):
    assert catalog.format in CatalogUpload.objects.first().file.name


@pytest.mark.freeze_time('2019-01-01')
def test_upload_date_saved_in_catalog_file(catalog):
    assert str(catalog.uploaded_at) in CatalogUpload.objects.first().file.name


def test_catalog_identifiers_unique(catalog):
    with pytest.raises(ValidationError):
        CatalogUpload.objects.create(node=catalog.node,
                                     format=CatalogUpload.FORMAT_JSON)


def test_catalog_can_only_have_valid_formats(node):
    with pytest.raises(ValidationError):
        catalog = CatalogUpload(format='inva', node=node)
        catalog.save()


def test_create_from_url_or_file(node):
    with open_catalog('simple.json') as sample:
        data_dict = {'format': 'json', 'node': node, 'file': sample}
        catalog = CatalogUpload.create_from_url_or_file(data_dict)
        assert catalog.file.read() == b'{"identifier": "test"}'


@pytest.mark.freeze_time('2019-01-01')
def test_catalog_uploaded_at(catalog):
    assert catalog.uploaded_at == timezone.now().date()


def test_xlsx_format_file_name(xlsx_catalog):
    name = xlsx_catalog.file.name.split('/')[-1]
    assert 'catalog' in name


def test_json_format_file_name(catalog):
    name = catalog.file.name.split('/')[-1]
    assert 'data' in name


def test_xlsx_format_file_name_no_data(xlsx_catalog):
    name = xlsx_catalog.file.name.split('/')[-1]
    assert 'data' not in name


def test_latest_catalog_saved(catalog):
    assert os.path.exists(os.path.join(settings.MEDIA_ROOT,
                                       'catalog',
                                       catalog.node.identifier,
                                       'data.json'))


def test_catalog_unique_by_date_and_node(catalog):
    with open_catalog('simple.json') as sample:
        with pytest.raises(IntegrityError):
            CatalogUpload.objects.create(node=catalog.node,
                                         format=CatalogUpload.FORMAT_JSON,
                                         file=File(sample))


def test_same_day_multiple_catalog_uploads(node):
    with open_catalog('simple.json') as sample:
        data_dict = {'format': 'json', 'node': node, 'file': sample}
        CatalogUpload.create_from_url_or_file(data_dict)

    with open_catalog('simple.json') as sample:
        data_dict = {'format': 'json', 'node': node, 'file': sample}
        CatalogUpload.create_from_url_or_file(data_dict)

    assert CatalogUpload.objects.count() == 1


def test_catalog_get_datasets(catalog):
    ids = [x['identifier'] for x in catalog.get_datasets()]

    assert ["125"] == ids


def test_validate_returns_error_message_if_catalog_is_not_valid(node):
    error_messages = [
        "'publisher' is a required property",
        "'title' is a required property",
        "'superThemeTaxonomy' is a required property",
        "'description' is a required property",
        "'Índice-precios-internos-basicos-al-por-mayor-desagregado-base-1993-anual.csv' "
        "is not valid under any of the given schemas",
    ]

    with open_catalog('data.json') as sample:
        data_dict = {'format': 'json', 'node': node, 'file': sample}
        catalog_upload = CatalogUpload.create_from_url_or_file(data_dict)
        validation_result = catalog_upload.validate()

    for error_message in error_messages:
        assert error_message in validation_result


def test_upload_file_permissions(catalog):
    # As per https://stackoverflow.com/questions/5337070/how-can-i-get-a-files-permission-mask
    mask = oct(os.stat(catalog.file.path)[stat.ST_MODE])[-3:]
    assert mask == '664'


def test_latest_file_permissions(catalog):
    path = os.path.join(settings.MEDIA_ROOT,
                        'catalog',
                        catalog.node.identifier,
                        'data.json')
    mask = oct(os.stat(path)[stat.ST_MODE])[-3:]
    assert mask == '664'
