# coding=utf-8
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models, transaction
from django.utils import timezone
from pydatajson import DataJson

from infra.apps.catalog.catalog_data_validator import CatalogDataValidator
from infra.apps.catalog.constants import CATALOG_ROOT
from infra.apps.catalog.models.node import Node


def catalog_file_path(instance, _filename=None):
    file_name = _file_name_for_format(instance)

    return os.path.join(CATALOG_ROOT,
                        instance.node.identifier,
                        f'{file_name}-{instance.uploaded_at}.{instance.format}')


def _file_name_for_format(catalog):
    names = {
        CatalogUpload.FORMAT_JSON: 'data',
        CatalogUpload.FORMAT_XLSX: 'catalog'
    }
    file_name = names[catalog.format]
    return file_name


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
        name = _file_name_for_format(instance)
        return os.path.join(CATALOG_ROOT,
                            instance.node.identifier,
                            f'{name}.{instance.format}')


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

    def validate(self):
        error_messages = []
        file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)

        try:
            data_json = DataJson(file_path)
        except KeyError:
            return ["No se puede validar el catálogo ingresado"]

        if not data_json.is_valid_catalog():
            error_report = data_json.validate_catalog()
            errors = error_report['error']['catalog']['errors']

            for dataset in error_report['error']['dataset']:
                errors += dataset['errors']

            error_messages = [error['message'] for error in errors]

        return error_messages
