import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_link_to_detail_page(user, distribution, logged_client):
    node = distribution.catalog
    node.admins.add(user)
    node.save()
    response = logged_client.get(reverse('catalog:node_distributions',
                                         kwargs={
                                             'node_id': node.id}
                                         ))
    detail_url = reverse('catalog:distribution_uploads', kwargs={
        'node_id': node.id,
        'identifier': distribution.identifier
    })
    assert detail_url in response.content.decode('utf-8')
