import os

from infra.apps.catalog.constants import CATALOG_ROOT
from infra.apps.catalog.storage.infra_storage import InfraStorage


def distribution_directory(instance):
    return os.path.join(CATALOG_ROOT,
                        instance.distribution.catalog.identifier,
                        'dataset',
                        instance.distribution.dataset_identifier,
                        'distribution',
                        instance.distribution.identifier,
                        'download')


class DistributionStorage(InfraStorage):
    def latest_file_path(self, instance):
        return os.path.join(distribution_directory(instance),
                            instance.distribution.file_name)
