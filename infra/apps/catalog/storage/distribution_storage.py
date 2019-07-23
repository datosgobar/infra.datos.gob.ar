import os

from infra.apps.catalog.constants import CATALOG_ROOT
from infra.apps.catalog.storage.catalog_storage import CustomCatalogStorage


def distribution_directory(instance):
    return os.path.join(CATALOG_ROOT,
                        instance.node.identifier,
                        'dataset',
                        instance.dataset_identifier,
                        'distribution',
                        instance.identifier,
                        'download')


class DistributionStorage(CustomCatalogStorage):
    def _latest_file_path(self, instance):
        name = instance.name.split('/')[-1]
        return os.path.join(distribution_directory(instance),
                            name)
