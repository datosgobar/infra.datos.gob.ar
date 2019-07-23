import pytest
from django.core.files import File

from infra.apps.catalog.models.distribution import Distribution
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog

pytestmark = pytest.mark.django_db


def test_upload_distribution_contains_distribution_id(catalog):
    with open_catalog('test_data.csv') as distribution:
        Distribution.objects.create(node=catalog.node,
                                    dataset_identifier='125',
                                    identifier='125.1',
                                    file=File(distribution))

    assert '125.1' in Distribution.objects.first().file.name
