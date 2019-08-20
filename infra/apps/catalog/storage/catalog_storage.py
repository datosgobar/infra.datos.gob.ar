from infra.apps.catalog.storage.infra_storage import InfraStorage
from infra.apps.catalog.storage.paths import catalog_path


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
