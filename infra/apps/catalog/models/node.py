from django.conf import settings
from django.db import models

from infra.apps.catalog.exceptions.catalog_not_uploaded_error import CatalogNotUploadedError


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
