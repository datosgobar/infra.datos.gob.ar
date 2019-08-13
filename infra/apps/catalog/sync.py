from django.core.exceptions import ValidationError

from infra.apps.catalog.exceptions.catalog_sync_error import CatalogSyncError
from infra.apps.catalog.models import Node


def sync_catalog(node_id):
    try:
        node = Node.objects.get(pk=node_id)
    except Node.DoesNotExist:
        raise CatalogSyncError("Catálogo consultado no existe")

    try:
        catalog = node.sync()
        return catalog.validate()
    except ValidationError as e:
        raise CatalogSyncError(f"Error de lectura del catálogo: {str(e)}")
    except FileNotFoundError:
        raise CatalogSyncError("No se encontró un catálogo en el file system para este nodo")
