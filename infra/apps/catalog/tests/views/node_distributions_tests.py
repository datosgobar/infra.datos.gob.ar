import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def give_user_edit_rights(user, node):
    node.admins.add(user)


def _call(client, distribution_upload, selected_dataset=None):
    url = reverse('catalog:node_distributions',
                  kwargs={'node_id': distribution_upload.distribution.catalog.id})
    if selected_dataset:
        url += '?dataset_identifier={}'.format(selected_dataset)
    return client.get(url)


def test_dataset_identifiers_in_context(logged_client, distribution_upload):
    response = _call(logged_client, distribution_upload)
    dataset_identifiers = [dataset[0] for dataset in response.context['dataset_list']]
    assert distribution_upload.distribution.dataset_identifier in dataset_identifiers


def url_dataset_is_selected_dataset(logged_client, distribution_upload):
    distribution_dataset_id = distribution_upload.distribution.dataset_identifier
    response = _call(logged_client, distribution_upload,
                     selected_dataset=distribution_upload.distribution.dataset_identifier)
    assert distribution_dataset_id == response.context['selected_dataset']