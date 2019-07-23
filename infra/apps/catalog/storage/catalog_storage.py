import os

from django.core.files.storage import FileSystemStorage

from infra.apps.catalog.constants import CATALOG_ROOT
from infra.apps.catalog.helpers.file_name_for_format import file_name_for_format


class CustomCatalogStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
        return name

    def save_as_latest(self, instance):
        path = self._latest_file_path(instance)
        self.save(path, instance.file)
        instance.file.seek(0)

    def _latest_file_path(self, instance):
        name = file_name_for_format(instance)
        return os.path.join(CATALOG_ROOT,
                            instance.node.identifier,
                            f'{name}.{instance.format}')
