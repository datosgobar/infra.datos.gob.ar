import pytest
from django.core.exceptions import ValidationError
from django.core.files import File

from infra.apps.catalog.models import CatalogUpload
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


def test_catalog_saves_to_identifier_path():
    catalog = CatalogUpload.objects.create(identifier='sspm', format='json')

    with open_catalog('data.json') as sample:
        catalog.file = File(sample)
        catalog.save()

    assert 'catalog/sspm/data.json' in CatalogUpload.objects.first().file.name


def test_catalog_identifiers_unique():
    CatalogUpload.objects.create(identifier='sspm', format='json')

    with pytest.raises(ValidationError):
        CatalogUpload.objects.create(identifier='sspm', format='xlsx')


def test_catalog_can_only_have_valid_formats():
    with pytest.raises(ValidationError):
        catalog = CatalogUpload(identifier='sspm', format='inva')
        catalog.save()


def test_create_from_url_or_file():
    with open_catalog('simple.json') as sample:
        data_dict = {'format': 'json', 'identifier': 'test', 'file': sample}
        catalog = CatalogUpload.create_from_url_or_file(data_dict)
        assert catalog.file.read() == b'{"identifier": "test"}'
