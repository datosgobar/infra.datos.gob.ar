from django.core.files import File
from pydatajson import DataJson
from pydatajson.writers import write_json_catalog, write_xlsx_catalog

from infra.apps.catalog.storage.infra_storage import InfraStorage
from infra.apps.catalog.storage.paths import catalog_path, absolute_catalog_path

class CustomCatalogStorage(InfraStorage):
    pass

class CustomJsonCatalogStorage(InfraStorage):
    def latest_file_path(self, instance):
        return catalog_path(instance.node.identifier, 'data.json')


class CustomExcelCatalogStorage(InfraStorage):
    def latest_file_path(self, instance):
        return catalog_path(instance.node.identifier, 'catalog.xlsx')
