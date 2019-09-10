from django.urls import reverse


def test_catalog_has_json(admin_client, catalog):
    response = admin_client.get(reverse('catalog:node', kwargs={'node_id': catalog.node.id}))

    assert response.context['has_json']


def test_catalog_has_xlsx(admin_client, xlsx_catalog):
    response = admin_client.get(reverse('catalog:node', kwargs={'node_id': xlsx_catalog.node.id}))

    assert response.context['has_xlsx']
