import os

from django.conf import settings

from infra.apps.catalog.constants import CATALOG_ROOT


def catalog_path(identifier, file_name):
    return os.path.join(CATALOG_ROOT,
                        identifier,
                        file_name)


def latest_json_catalog_path(node_id):
    return os.path.join(settings.MEDIA_ROOT,
                        catalog_path(node_id, 'data.json'))
