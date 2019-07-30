# coding=utf-8
from django import forms

from infra.apps.catalog.models import CatalogUpload, Distribution

FORMAT_OPTIONS = [
        ('json', 'JSON'),
        ('xlsx', 'XLSX')
    ]


class CatalogForm(forms.ModelForm):
    class Meta:
        model = CatalogUpload
        fields = ['format', 'file']

    file = forms.FileField(required=False)
    format = forms.CharField(label='Formato', widget=forms.Select(choices=FORMAT_OPTIONS))
    url = forms.URLField(required=False)


class DistributionForm(forms.ModelForm):
    class Meta:
        model = Distribution
        fields = ['distribution_identifier', 'file']

    file = forms.FileField(required=False)
    file_name = forms.CharField(required=True)
    url = forms.URLField(required=False)
    distribution_identifier = forms.CharField()

    def __init__(self, *args, **kwargs):
        node = kwargs.pop('node')
        super(DistributionForm, self).__init__(*args, **kwargs)
        latest = node.get_latest_catalog_upload()
        datasets = [(x['identifier'], x['identifier']) for x in latest.get_datasets()]
        self.fields['dataset_identifier'] = \
            forms.ChoiceField(choices=datasets, initial=self.instance.dataset_identifier)
        self.fields['file_name'].initial = self.instance.file_name
