from tempfile import NamedTemporaryFile

import pytest
from django.core.files import File
from django.db import IntegrityError

from infra.apps.catalog.models import Node, CatalogUpload

pytestmark = pytest.mark.django_db


def test_node_unique_identifier(node):
    with pytest.raises(IntegrityError):
        Node.objects.create(identifier=node.identifier)


def test_node_representation_has_identifier(node):
    assert node.identifier in str(node)


def get_latest_catalog(node):
    node.catalogupload_set.create(format=CatalogUpload.FORMAT_JSON,
                                            file=File(NamedTemporaryFile()))
    catalog = node.catalogupload_set.create(format=CatalogUpload.FORMAT_JSON,
                                            file=File(NamedTemporaryFile()))

    assert node.get_latest_catalog_upload().id == catalog.id
