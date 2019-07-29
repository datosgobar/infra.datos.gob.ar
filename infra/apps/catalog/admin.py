# coding=utf-8

from django.contrib import admin

from infra.apps.catalog import models


class CatalogAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Distribution)
class DistributionAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.CatalogUpload, CatalogAdmin)
