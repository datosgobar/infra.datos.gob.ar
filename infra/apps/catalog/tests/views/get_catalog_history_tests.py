import datetime

from django.core.files import File
from django.urls import reverse

from infra.apps.catalog.models import CatalogUpload
from infra.apps.catalog.tests.helpers.open_catalog import open_catalog


def test_catalog_history_has_node(admin_client, catalog):
    response = admin_client.get(reverse('catalog:catalog_history', kwargs={'node_id': catalog.node.id}))

    assert response.context['node']


def test_catalog_history_has_object_list(admin_client, catalog):
    response = admin_client.get(reverse('catalog:catalog_history', kwargs={'node_id': catalog.node.id}))

    assert response.context['object_list']


def test_catalog_history_has_object_list_ordered_by_date_descendent(admin_client, catalog):
    lastweek = datetime.datetime.now() - datetime.timedelta(days=7)
    CatalogUpload.objects.filter(pk=catalog.pk).update(uploaded_at=lastweek)
    with open_catalog('data.json') as catalog_fd:
        model = CatalogUpload(format=CatalogUpload.FORMAT_JSON,
                              json_file=File(catalog_fd),
                              node=catalog.node)
        model.save()

    response = admin_client.get(reverse('catalog:catalog_history', kwargs={'node_id': catalog.node.id}))
    catalogs = response.context['object_list']
    for i in range(len(catalogs) - 1):
        assert catalogs[i].uploaded_at > catalogs[i+1].uploaded_at
