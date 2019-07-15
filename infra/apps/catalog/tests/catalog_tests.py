import pytest
from django.core.files import File
from django.db import IntegrityError

from infra.apps.catalog.models import Catalog
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

PYTESTMARK = pytest.mark.django_db


def test_catalog_saves_to_identifier_path():
    catalog = Catalog.objects.create(identifier='sspm', format='json')

    with open_catalog('data.json') as sample:
        catalog.file = File(sample)
        catalog.save()

    assert 'catalogs/sspm/data.json' in Catalog.objects.first().file.name


def test_catalog_identifiers_unique():
    Catalog.objects.create(identifier='sspm', format='json')

    with pytest.raises(IntegrityError):
        Catalog.objects.create(identifier='sspm', format='xlsx')
