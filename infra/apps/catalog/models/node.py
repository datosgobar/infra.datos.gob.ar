from django.conf import settings
from django.db import models

from infra.apps.catalog.exceptions.catalog_not_uploaded_error import CatalogNotUploadedError
from infra.apps.catalog.storage.paths import latest_json_catalog_path
from infra.apps.catalog.helpers.temp_uploaded_file import temp_uploaded_file
from infra.apps.catalog.validator.catalog_data_validator import CatalogDataValidator


class Node(models.Model):
    identifier = models.CharField(max_length=20, unique=True)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.identifier

    def get_latest_catalog_upload(self):
        catalog = self.catalogupload_set.order_by('uploaded_at').last()
        if catalog is None:
            raise CatalogNotUploadedError

        return catalog

    def sync(self):
        path = latest_json_catalog_path(self.identifier)

        catalog_data = CatalogDataValidator().get_and_validate_data({
            'file': temp_uploaded_file(open(path, 'rb')),
            'node': self,
            'format': 'json',
        })

        return self.catalogupload_set.create(**catalog_data)
