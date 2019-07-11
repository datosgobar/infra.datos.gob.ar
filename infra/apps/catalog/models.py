# coding=utf-8
import os

from django.core.files.storage import FileSystemStorage
from django.db import models

def catalog_file_path(instance, filename=None):
    return f'catalogs/{instance.identifier}/data.{instance.format}'


class CustomCatalogStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
        return name


class Catalog(models.Model):
    identifier = models.CharField(default='', max_length=20, unique=True)
    format = models.CharField(max_length=4, blank=False, null=False)
    file = models.FileField(upload_to=catalog_file_path, blank=True, null=True,
                            storage=CustomCatalogStorage())

    def __str__(self):
        return self.identifier
