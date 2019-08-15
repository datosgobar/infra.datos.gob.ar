# coding=utf-8
import os

from django.conf import settings
from django.core.files import File
from django.db import models, transaction
from django.utils import timezone
from pydatajson import DataJson
from pydatajson.writers import write_xlsx_catalog, write_json_catalog

from infra.apps.catalog.validator.catalog_data_validator import CatalogDataValidator
from infra.apps.catalog.helpers.file_name_for_format import file_name_for_format
from infra.apps.catalog.storage.catalog_storage import CustomCatalogStorage
from infra.apps.catalog.constants import CATALOG_ROOT


def catalog_file_path(instance, format, _filename=None):
    file_name = file_name_for_format(format)

    return os.path.join(CATALOG_ROOT,
                        instance.node.identifier,
                        f'{file_name}-{instance.uploaded_at}.{format}')


def json_catalog_file_path(instance, _filename=None):
    return catalog_file_path(instance, 'json')


def xlsx_catalog_file_path(instance, _filename=None):
    return catalog_file_path(instance, 'xlsx')


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

    node = models.ForeignKey(to='Node', on_delete=models.CASCADE, unique_for_date='uploaded_at')
    format = models.CharField(max_length=4, blank=False, null=False, choices=FORMAT_OPTIONS)
    uploaded_at = models.DateField(auto_now_add=True)
    json_file = models.FileField(upload_to=json_catalog_file_path,
                                 storage=CustomCatalogStorage(),
                                 null=True, blank=True)
    xlsx_file = models.FileField(upload_to=xlsx_catalog_file_path,
                                 storage=CustomCatalogStorage(),
                                 null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(CatalogUpload, self).__init__(*args, **kwargs)
        self._datajson = None

    @property
    def datajson(self):
        if not self._datajson:
            self._datajson = DataJson(self.json_file.file.name)

        return self._datajson

    def __str__(self):
        return self.node.identifier

    def clean(self):
        # No existen ninguno de los dos archivos aun (no hubo save)
        if not self.json_file:
            data = DataJson(self.xlsx_file.path)
            path = os.path.join(settings.MEDIA_ROOT, xlsx_catalog_file_path(self))
            write_json_catalog(data, path)
            with open(path, 'r') as json_file:
                self.json_file = File(json_file)

        elif not self.xlsx_file:
            data = DataJson(self.json_file.path)
            path = os.path.join(settings.MEDIA_ROOT, json_catalog_file_path(self))
            write_xlsx_catalog(data, path)
            with open(path, 'r') as xlsx_file:
                self.xlsx_file = File(xlsx_file)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        super(CatalogUpload, self).save(force_insert, force_update, using, update_fields)
        self.json_file.storage.save_as_latest(self)
        self.xlsx_file.storage.save_as_latest(self)

    @classmethod
    def create_from_url_or_file(cls, raw_data):
        data = CatalogDataValidator().get_and_validate_data(raw_data)
        catalog = cls.upsert(data)

        if not data.get('file').closed:
            data.get('file').close()

        return catalog

    @classmethod
    def upsert(cls, data):
        with transaction.atomic():
            cls.objects.filter(node=data['node'], uploaded_at=timezone.now().date()).delete()
            catalog = cls.objects.create(**data)
        return catalog

    def get_datasets(self):
        return self.datajson.get_datasets()

    def validate(self):
        error_messages = []
        file_path = os.path.join(settings.MEDIA_ROOT, self.json_file.name)

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
