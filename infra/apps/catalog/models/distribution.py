import os
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import models
from django.utils import timezone

from infra.apps.catalog.context_managers import distribution_file_handler
from infra.apps.catalog.helpers.temp_file_from_url import temp_file_from_url
from infra.apps.catalog.models.node import Node
from infra.apps.catalog.storage.distribution_storage import \
    DistributionStorage, distribution_directory


def distribution_file_path(instance, _filename=None):
    directory = distribution_directory(instance)
    decomposed_name = instance.distribution.file_name.rsplit('.', maxsplit=1)
    final_name = f'{decomposed_name[0]}-{instance.uploaded_at}'
    if len(decomposed_name) > 1:
        # filename includes extension
        final_name += f'.{decomposed_name[-1]}'
    return os.path.join(directory, final_name)


class DistributionManager(models.Manager):

    def upsert_upload(self, node, data):
        distribution, created = self.get_or_create(
            identifier=data['distribution_identifier'],
            catalog=node,
            defaults={'dataset_identifier': data['dataset_identifier'],
                      'file_name': data['file_name']}
        )

        if not created and data['file_name'] != distribution.file_name:
            same_day_version = distribution.distributionupload_set \
                .get(uploaded_at=timezone.now().date(),)

            file_path_without_date = os.path.join(settings.MEDIA_ROOT, same_day_version.file_path())
            file_path_with_date = \
                os.path.join(settings.MEDIA_ROOT, same_day_version.file_path(with_date=True))
            os.remove(file_path_without_date)
            os.remove(file_path_with_date)

            distribution.dataset_identifier = data['dataset_identifier']
            distribution.file_name = data['file_name']
            distribution.save()

        file = data.get('file') or File(temp_file_from_url(data['url']))
        upload, _ = distribution.distributionupload_set.update_or_create(
            uploaded_at=timezone.now().date(),
            defaults={'file': file}

        )
        return upload


class Distribution(models.Model):
    objects = DistributionManager()

    catalog = models.ForeignKey(to=Node, on_delete=models.CASCADE,
                                unique_for_date='uploaded_at')
    dataset_identifier = models.CharField(max_length=64)
    file_name = models.CharField(max_length=800)
    identifier = models.CharField(max_length=64)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.catalog.get_latest_catalog_upload()  # Validación de que hay un upload
        super(Distribution, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.identifier} ({self.catalog.identifier})'


class DistributionUpload(models.Model):
    distribution = models.ForeignKey(to=Distribution, on_delete=models.CASCADE)
    uploaded_at = models.DateField(auto_now_add=True)
    file = models.FileField(upload_to=distribution_file_path,
                            storage=DistributionStorage(),
                            max_length=1000)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(DistributionUpload, self).save(force_insert, force_update, using, update_fields)
        self.file.storage.save_as_latest(self)

    @classmethod
    def update_or_create(cls, distribution, file):
        same_day_version = cls.get_version_from_same_day(distribution)
        with distribution_file_handler(same_day_version, distribution.file_name):
            upload, _ = cls.objects.update_or_create(
                uploaded_at=timezone.now().date(),
                distribution=distribution,
                defaults={'file': file}
            )

        return upload

    @classmethod
    def get_version_from_same_day(cls, distribution):
        versions_from_today = distribution.distributionupload_set \
            .filter(uploaded_at=timezone.now().date())
        return versions_from_today.first()

    def __str__(self):
        return f'{self.distribution.identifier} ({self.uploaded_at})'

    def file_name_with_date(self):
        path = Path(self.file.name)
        return path.name

    def file_path(self, with_date=False):
        path = Path(self.file.name)
        filename = self.file_name_with_date() if with_date else self.distribution.file_name
        return path.with_name(filename)
