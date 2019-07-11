# coding=utf-8
from django.core.exceptions import ValidationError
from django.forms import ModelForm, URLField, CharField, Select

from infra.apps.catalog.models import Catalog


class CatalogForm(ModelForm):

    FORMAT_OPTIONS = [
        ('json', 'JSON'),
        ('xlsx', 'XLSX')
    ]

    class Meta:
        model = Catalog
        fields = ['format', 'file']

    format = CharField(label='Formato', widget=Select(choices=FORMAT_OPTIONS))
    url = URLField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        form_format = cleaned_data.get('format')
        file = cleaned_data.get('file')
        url = cleaned_data.get('url')

        if not file and not url:
            raise ValidationError("Se tiene que ingresar por lo menos un archivo o un URL válido")

        if file and url:
            raise ValidationError("No se pueden ingresar un archivo y un URL a la vez")

        file_format = (url or file.name).split('.')[-1]
        if form_format != file_format:
            raise ValidationError("El formato ingresado no coincide con el del archivo")
