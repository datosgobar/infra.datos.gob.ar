from shutil import copy2

import pytest
from django.core.exceptions import ValidationError

from infra.apps.catalog.sync import sync_catalog
from infra.apps.catalog.tests.helpers.open_catalog import catalog_path


def test_sync_valid_catalog(node, catalog_dest):
    copy2(catalog_path('data.json'), catalog_dest)
    node.sync()
    assert node.catalogupload_set.count() == 1


def test_sync_catalog_nothing_uploaded(node):
    with pytest.raises(FileNotFoundError):
        node.sync()


def test_sync_invalid_catalog(node, catalog_dest):
    copy2(catalog_path('catalogo-justicia.xlsx'), catalog_dest)
    with pytest.raises(ValidationError):
        node.sync()


def test_sync_catalog_returns_errors(node, catalog_dest):
    copy2(catalog_path('data.json'), catalog_dest)
    assert sync_catalog(node.id)
