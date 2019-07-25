import os

from infra.apps.catalog.constants import CATALOG_ROOT
from infra.apps.catalog.helpers.file_name_for_format import file_name_for_format
from infra.apps.catalog.storage.infra_storage import InfraStorage


class CustomCatalogStorage(InfraStorage):
    def latest_file_path(self, instance):
        name = file_name_for_format(instance)
        return os.path.join(CATALOG_ROOT,
                            instance.node.identifier,
                            f'{name}.{instance.format}')
