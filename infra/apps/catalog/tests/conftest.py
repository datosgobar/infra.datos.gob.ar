import pytest
from django.core.files import File

from infra.apps.catalog.models import CatalogUpload, Node
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog


@pytest.fixture
def catalog():
    with open_catalog('data.json') as catalog_fd:
        model = CatalogUpload(identifier='test_catalog',
                              format=CatalogUpload.FORMAT_JSON,
                              file=File(catalog_fd))
        model.save()

    return model


@pytest.fixture
def node():
    return Node.objects.create(identifier='test_id')
