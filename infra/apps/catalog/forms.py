# coding=utf-8
from django.forms import ModelForm, URLField, CharField, Select

from infra.apps.catalog.models import Catalog


class CatalogForm(ModelForm):

    FORMAT_OPTIONS = [
        ('json', 'JSON'),
        ('xlsx', 'XLSX')
    ]

    class Meta:
        model = Catalog
        fields = ['format', 'file', 'identifier']

    format = CharField(label='Formato', widget=Select(choices=FORMAT_OPTIONS))
    url = URLField(required=False)
