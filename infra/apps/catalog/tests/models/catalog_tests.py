import pytest
from django.core.exceptions import ValidationError
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
    assert str(catalog.uploaded_at.date()) in CatalogUpload.objects.first().file.name


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
    assert catalog.uploaded_at.date() == timezone.now().date()
