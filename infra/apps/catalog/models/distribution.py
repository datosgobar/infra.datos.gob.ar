import os
from pathlib import Path

from django.core.files import File
from django.db import models

from infra.apps.catalog.helpers.temp_file_from_url import temp_file_from_url
from infra.apps.catalog.models.node import Node
from infra.apps.catalog.storage.distribution_storage import \
    DistributionStorage, distribution_directory


def distribution_file_path(instance, _filename=None):
    directory = distribution_directory(instance)
    extension = instance.file.name.split('/')[-1].rsplit('.', maxsplit=1)[-1]
    final_name = f'{instance.file_name}-{instance.uploaded_at}.{extension}'
    return os.path.join(directory, final_name)


class Distribution(models.Model):
    node = models.ForeignKey(to=Node, on_delete=models.CASCADE, unique_for_date='uploaded_at')
    uploaded_at = models.DateField(auto_now_add=True)
    dataset_identifier = models.CharField(max_length=64)
    file_name = models.CharField(max_length=800)
    identifier = models.CharField(max_length=64)
    file = models.FileField(upload_to=distribution_file_path,
                            storage=DistributionStorage(),
                            max_length=1000)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.node.get_latest_catalog_upload()  # Validación de que hay un upload
        super(Distribution, self).save(force_insert, force_update, using, update_fields)
        self.file.storage.save_as_latest(self)

    @classmethod
    def create_from_url(cls, raw_data):
        file = File(temp_file_from_url(raw_data['url']))
        return cls.objects.create(file=file,
                                  node=raw_data['node'],
                                  dataset_identifier=raw_data['dataset_identifier'],
                                  file_name=raw_data['file_name'],
                                  identifier=raw_data['identifier'])

    def __str__(self):
        return self.identifier

    def file_name_with_date(self):
        path = Path(self.file.name)
        return path.stem
