# coding=utf-8
import os

from django.core.files.storage import FileSystemStorage
from django.db import models

from infra.apps.catalog.catalog_data_validator import CatalogDataValidator
from infra.apps.catalog.models.node import Node
from infra.apps.catalog.constants import CATALOG_ROOT


def catalog_file_path(instance, _filename=None):
    file_name_for_format = {
        CatalogUpload.FORMAT_JSON: 'data',
        CatalogUpload.FORMAT_XLSX: 'catalog'
    }

    file_name = file_name_for_format[instance.format]

    return os.path.join(CATALOG_ROOT,
                        instance.node.identifier,
                        f'{file_name}-{instance.uploaded_at}.{instance.format}')


class CustomCatalogStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
        return name


class CatalogUpload(models.Model):

    FORMAT_JSON = 'json'
    FORMAT_XLSX = 'xlsx'
    FORMAT_OPTIONS = [
        (FORMAT_JSON, 'JSON'),
        (FORMAT_XLSX, 'XLSX'),
    ]

    node = models.ForeignKey(to=Node, on_delete=models.CASCADE)
    format = models.CharField(max_length=4, blank=False, null=False, choices=FORMAT_OPTIONS)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=catalog_file_path,
                            storage=CustomCatalogStorage())

    def __str__(self):
        return self.node.identifier

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        super(CatalogUpload, self).save(force_insert, force_update, using, update_fields)

    @classmethod
    def create_from_url_or_file(cls, raw_data):
        data = CatalogDataValidator().get_and_validate_data(raw_data)
        catalog = cls.objects.create(**data)

        if not data.get('file').closed:
            data.get('file').close()

        return catalog
