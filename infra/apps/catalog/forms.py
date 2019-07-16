# coding=utf-8
from django.forms import ModelForm, URLField, CharField, Select

from infra.apps.catalog.catalog_data_validator import CatalogDataValidator
from infra.apps.catalog.models import Catalog

FORMAT_OPTIONS = [
        ('json', 'JSON'),
        ('xlsx', 'XLSX')
    ]


class AbstractCatalogForm(ModelForm):
    class Meta:
        model = Catalog
        fields = ['format', 'file', 'identifier']

    def clean(self):
        cleaned_data = super().clean()
        form_file = cleaned_data.get('file')
        form_url = cleaned_data.get('url')
        form_format = cleaned_data.get('format')

        validator = CatalogDataValidator()
        validator.validate_file_and_url_fields(form_file, form_format, form_url)


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
