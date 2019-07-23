import os

import pytest
import requests_mock
from django.conf import settings
from django.core.files import File

from infra.apps.catalog.models import CatalogUpload, Node, Distribution
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog


@pytest.fixture
def catalog():
    with open_catalog('data.json') as catalog_fd:
        model = CatalogUpload(format=CatalogUpload.FORMAT_JSON,
                              file=File(catalog_fd),
                              node=_node())
        model.save()

    return model


@pytest.fixture
def xlsx_catalog():
    with open_catalog('catalogo-justicia.xlsx') as catalog_fd:
        model = CatalogUpload(format=CatalogUpload.FORMAT_XLSX,
                              file=File(catalog_fd),
                              node=_node())
        model.save()

    return model


@pytest.fixture
def node():
    return _node()


@pytest.fixture
def mock_request():
    return requests_mock.mock()


def _node():
    return Node.objects.create(identifier='test_id')


@pytest.fixture(scope='session', autouse=True)
def media_root():
    yield
    # Will be executed after the last test
    import shutil
    shutil.rmtree(settings.MEDIA_ROOT)
    os.mkdir(settings.MEDIA_ROOT)


@pytest.fixture
def distribution():
    with open_catalog('test_data.csv') as distribution_fd:
        model = Distribution(file=File(distribution_fd),
                             node=_node(),
                             identifier="125.1",
                             dataset_identifier="125")
        model.save()

    return model
