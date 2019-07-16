# coding=utf-8
from django.forms import ModelForm, URLField, CharField, Select

from infra.apps.catalog.models import Catalog

FORMAT_OPTIONS = [
        ('json', 'JSON'),
        ('xlsx', 'XLSX')
    ]


class AbstractCatalogForm(ModelForm):
    class Meta:
        model = Catalog
        fields = ['format', 'file', 'identifier']


class CatalogForm(AbstractCatalogForm):
    class Meta:
        model = Catalog
        fields = ['format', 'file', 'identifier']

    format = CharField(label='Formato', widget=Select(choices=FORMAT_OPTIONS))
    url = URLField(required=False)


class AdminCatalogForm(AbstractCatalogForm):
    class Meta:
        model = Catalog
        fields = ['format', 'file', 'identifier']

    format = CharField(widget=Select(choices=FORMAT_OPTIONS))
