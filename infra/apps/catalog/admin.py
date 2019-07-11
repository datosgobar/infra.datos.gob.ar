# coding=utf-8

from django.contrib import admin

from infra.apps.catalog import models

admin.site.register(models.Catalog)
