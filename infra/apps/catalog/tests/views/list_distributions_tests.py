import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_link_to_detail_page(user, distribution, logged_client):
    node = distribution.node
    node.admins.add(user)
    node.save()
    response = logged_client.get(reverse('catalog:node_distributions',
                                         kwargs={
                                             'node_id': distribution.node.id}
                                         ))
    detail_url = reverse('catalog:distribution_uploads', kwargs={
        'node_id': distribution.node.id,
        'identifier': distribution.identifier
    })
    assert detail_url in response.content.decode('utf-8')


def test_distribution_list_download_link(user, distribution, logged_client):
    node = distribution.node
    node.admins.add(user)
    node.save()
    response = logged_client.get(reverse('catalog:node_distributions',
                                         kwargs={
                                             'node_id': distribution.node.id}
                                         ))
    href = '/media/catalog/test_id/dataset/125/distribution/125.1' \
           '/download/test_data.csv'
    filename = 'test_data.csv'
    download_anchor = f'<a href="{href}" download="{filename}">' \
                      f'{filename}</a>'
    assert download_anchor in response.content.decode('utf-8')
