import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def give_user_edit_rights(user, node):
    node.admins.add(user)


def _call(client, distribution):
    return client.get(reverse('catalog:node_distributions',
                              kwargs={'node_id': distribution.catalog.id}))


def test_dataset_identifiers_in_page(logged_client, distribution):
    response = _call(logged_client, distribution)
    assert distribution.catalog.identifier in response.content.decode('utf-8')