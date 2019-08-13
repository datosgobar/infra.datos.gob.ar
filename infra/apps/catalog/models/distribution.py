import os
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import models
from django.utils import timezone

from infra.apps.catalog.helpers.temp_file_from_url import temp_file_from_url
from infra.apps.catalog.models.node import Node
from infra.apps.catalog.storage.distribution_storage import \
    DistributionStorage, distribution_directory


def distribution_file_path(instance, _filename=None):
    directory = distribution_directory(instance)
    decomposed_name = instance.file_name.rsplit('.', maxsplit=1)
    final_name = f'{decomposed_name[0]}-{instance.uploaded_at}'
    if len(decomposed_name) > 1:
        # filename includes extension
        final_name += f'.{decomposed_name[-1]}'
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
    def update_or_create(cls, raw_data):
        file = raw_data.get('file') or File(temp_file_from_url(raw_data['url']))
        distribution, _ = cls.objects.update_or_create(
            node=raw_data['node'],
            identifier=raw_data['distribution_identifier'],
            uploaded_at=timezone.now().date(),
            defaults={'dataset_identifier': raw_data['dataset_identifier'],
                      'file': file,
                      'file_name': raw_data['file_name']}
        )
        return distribution

    @classmethod
    def get_version_from_same_day(cls, node, distribution_identifier):
        versions_from_today = Distribution.objects.filter(
            identifier=distribution_identifier,
            node=node,
            uploaded_at=timezone.now().date())
        return versions_from_today[0] if versions_from_today else None

    def __str__(self):
        return self.identifier

    def file_name_with_date(self):
        path = Path(self.file.name)
        return path.name

    def file_path(self, with_date=False):
        path = Path(self.file.name)
        return path.with_name(self.file_name_with_date() if with_date else self.file_name)
