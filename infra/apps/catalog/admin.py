# coding=utf-8

from django.contrib import admin

from infra.apps.catalog import models
from infra.apps.catalog.forms import AdminCatalogForm


class CatalogAdmin(admin.ModelAdmin):
    form = AdminCatalogForm


admin.site.register(models.CatalogUpload, CatalogAdmin)
