# coding=utf-8

from django.contrib import admin

from infra.apps.catalog import models
from infra.apps.catalog.forms import CatalogForm


class CatalogAdmin(admin.ModelAdmin):
    form = CatalogForm


@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.CatalogUpload, CatalogAdmin)
