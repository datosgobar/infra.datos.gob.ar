import pytest
from django.core.exceptions import ValidationError

from infra.apps.catalog.models import CatalogUpload
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


def test_catalog_saves_to_identifier_path(catalog):
    path = f'catalog/{catalog.identifier}/data.json'
    assert path in CatalogUpload.objects.first().file.name


def test_catalog_identifiers_unique(catalog):
    with pytest.raises(ValidationError):
        CatalogUpload.objects.create(identifier=catalog.identifier,
                                     format=CatalogUpload.FORMAT_JSON)


def test_catalog_can_only_have_valid_formats():
    with pytest.raises(ValidationError):
        catalog = CatalogUpload(identifier='sspm', format='inva')
        catalog.save()


def test_create_from_url_or_file():
    with open_catalog('simple.json') as sample:
        data_dict = {'format': 'json', 'identifier': 'test', 'file': sample}
        catalog = CatalogUpload.create_from_url_or_file(data_dict)
        assert catalog.file.read() == b'{"identifier": "test"}'
