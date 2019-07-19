import pytest
from django.db import IntegrityError

from infra.apps.catalog.models import Node

pytestmark = pytest.mark.django_db


def test_node_unique_identifier(node):
    with pytest.raises(IntegrityError):
        Node.objects.create(identifier=node.identifier)


def test_node_representation_has_identifier(node):
    assert node.identifier in str(node)
