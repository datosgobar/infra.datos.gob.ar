from django.core.exceptions import ValidationError

from infra.apps.catalog.models import Node


def sync_catalog(node_id):
    try:
        node = Node.objects.get(pk=node_id)
    except Node.DoesNotExist:
        return ["Catálogo consultado no existe"]

    try:
        node.sync()
    except ValidationError as e:
        return [f"Error de lectura del catálogo: {str(e)}"]
    except FileNotFoundError:
        return ["No se encontró un catálogo en el file system para este nodo"]

    return []
