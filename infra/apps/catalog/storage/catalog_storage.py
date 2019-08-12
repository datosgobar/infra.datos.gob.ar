from infra.apps.catalog.helpers.file_name_for_format import file_name_for_format
from infra.apps.catalog.storage.infra_storage import InfraStorage
from infra.apps.catalog.storage.paths import catalog_path


class CustomCatalogStorage(InfraStorage):
    def latest_file_path(self, instance):
        name = file_name_for_format(instance)
        return catalog_path(instance.node.identifier,
                            f'{name}.{instance.format}')
