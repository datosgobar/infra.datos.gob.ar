import os

from django.db import models

from infra.apps.catalog.models.node import Node
from infra.apps.catalog.storage.distribution_storage import \
    DistributionStorage, distribution_directory


def distribution_file_path(instance, _filename=None):
    directory = distribution_directory(instance)
    name, extension = instance.file.name.split('/')[-1].rsplit('.', maxsplit=1)
    final_name = f'{name}-{instance.uploaded_at}.{extension}'
    return os.path.join(directory, final_name)


class Distribution(models.Model):
    node = models.ForeignKey(to=Node, on_delete=models.CASCADE, unique_for_date='uploaded_at')
    uploaded_at = models.DateField(auto_now_add=True)
    dataset_identifier = models.CharField(max_length=64)
    identifier = models.CharField(max_length=64)
    file = models.FileField(upload_to=distribution_file_path,
                            storage=DistributionStorage())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.node.get_latest_catalog_upload()  # Validación de que hay un upload
        super(Distribution, self).save(force_insert, force_update, using, update_fields)
