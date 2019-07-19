# coding=utf-8
from django import forms

from infra.apps.catalog.models import CatalogUpload

FORMAT_OPTIONS = [
        ('json', 'JSON'),
        ('xlsx', 'XLSX')
    ]


class CatalogForm(forms.ModelForm):
    class Meta:
        model = CatalogUpload
        fields = ['format', 'file', 'node']

    file = forms.FileField(required=False)
    format = forms.CharField(label='Formato', widget=forms.Select(choices=FORMAT_OPTIONS))
    url = forms.URLField(required=False)
