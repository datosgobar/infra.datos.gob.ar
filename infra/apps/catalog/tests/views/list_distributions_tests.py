import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_link_to_detail_page(distribution, client):
    response = client.get(reverse('catalog:node_distributions',
                                  kwargs={
                                      'node_id': distribution.node.id}
                                  ))
    detail_url = reverse('catalog:distribution_uploads', kwargs={
        'node_id': distribution.node.id,
        'identifier': distribution.identifier
    })
    assert detail_url in response.content.decode('utf-8')
