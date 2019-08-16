from django.core.files import File
from pydatajson import DataJson
from pydatajson.writers import write_json_catalog, write_xlsx_catalog

from infra.apps.catalog.storage.infra_storage import InfraStorage
from infra.apps.catalog.storage.paths import catalog_path, absolute_catalog_path


class CustomCatalogStorage(InfraStorage):
    pass


class CustomJsonCatalogStorage(InfraStorage):
    def save_as_latest(self, instance):
        path = self.latest_file_path(instance)
        self.save(path, instance.json_file)
        instance.json_file.seek(0)

    def latest_file_path(self, instance):
        return catalog_path(instance.node.identifier, 'data.json')


class CustomExcelCatalogStorage(InfraStorage):
    def save_as_latest(self, instance):
        path = self.latest_file_path(instance)
        self.save(path, instance.xlsx_file)
        instance.xlsx_file.seek(0)

    def latest_file_path(self, instance):
        return catalog_path(instance.node.identifier, 'catalog.xlsx')
