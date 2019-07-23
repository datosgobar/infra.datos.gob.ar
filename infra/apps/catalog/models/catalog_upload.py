# coding=utf-8
import os

from django.db import models, transaction
from django.utils import timezone
from pydatajson import DataJson

from infra.apps.catalog.validator.catalog_data_validator import CatalogDataValidator
from infra.apps.catalog.helpers.file_name_for_format import file_name_for_format
from infra.apps.catalog.models.node import Node
from infra.apps.catalog.constants import CATALOG_ROOT
from infra.apps.catalog.storage.catalog_storage import CustomCatalogStorage


def catalog_file_path(instance, _filename=None):
    file_name = file_name_for_format(instance)

    return os.path.join(CATALOG_ROOT,
                        instance.node.identifier,
                        f'{file_name}-{instance.uploaded_at}.{instance.format}')


class CatalogUpload(models.Model):
    class Meta:
        unique_together = (
            ('node', 'uploaded_at')
        )

    FORMAT_JSON = 'json'
    FORMAT_XLSX = 'xlsx'
    FORMAT_OPTIONS = [
        (FORMAT_JSON, 'JSON'),
        (FORMAT_XLSX, 'XLSX'),
    ]

    node = models.ForeignKey(to=Node, on_delete=models.CASCADE, unique_for_date='uploaded_at')
    format = models.CharField(max_length=4, blank=False, null=False, choices=FORMAT_OPTIONS)
    uploaded_at = models.DateField(auto_now_add=True)
    file = models.FileField(upload_to=catalog_file_path,
                            storage=CustomCatalogStorage())

    def __init__(self, *args, **kwargs):
        super(CatalogUpload, self).__init__(*args, **kwargs)
        self._datajson = None

    @property
    def datajson(self):
        if not self._datajson:
            self._datajson = DataJson(self.file.file.name)

        return self._datajson

    def __str__(self):
        return self.node.identifier

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        super(CatalogUpload, self).save(force_insert, force_update, using, update_fields)
        self.file.storage.save_as_latest(self)

    @classmethod
    def create_from_url_or_file(cls, raw_data):
        data = CatalogDataValidator().get_and_validate_data(raw_data)
        with transaction.atomic():
            cls.objects.filter(node=data['node'], uploaded_at=timezone.now().date()).delete()
            catalog = cls.objects.create(**data)

        if not data.get('file').closed:
            data.get('file').close()

        return catalog

    def get_datasets(self):
        return self.datajson.get_datasets()
