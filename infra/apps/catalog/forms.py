# coding=utf-8
from dal import autocomplete
from django import forms
from django.urls import reverse

from infra.apps.catalog.models import CatalogUpload, Distribution

FORMAT_OPTIONS = [
        ('json', 'JSON'),
        ('xlsx', 'XLSX')
    ]


class CatalogForm(forms.ModelForm):
    class Meta:
        model = CatalogUpload
        fields = ['format', 'file']

    file = forms.FileField(required=False,
                           widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    format = forms.CharField(label='Formato', widget=forms.Select(attrs={'class': 'form-control'},
                                                                  choices=FORMAT_OPTIONS))
    url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))


class DistributionForm(forms.ModelForm):
    class Meta:
        model = Distribution
        fields = ['distribution_identifier', 'file']

    file = forms.FileField(required=False,
                           widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    file_name = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    distribution_identifier = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        node = kwargs.pop('node')
        latest = node.get_latest_catalog_upload()
        super(DistributionForm, self).__init__(*args, **kwargs)

        dist_identifiers = []
        initial_identifier = ''
        for dataset in latest.get_datasets():
            identifier = dataset['title'] + " - " + dataset['identifier']
            dist_identifiers.append(identifier)
            if dataset['identifier'] == self.instance.dataset_identifier:
                initial_identifier = dataset['identifier']

        self.fields['dataset_identifier'] = \
            forms.ModelChoiceField(
                queryset=Distribution.objects.all(),
                # choice_list=dist_identifiers,
                # initial=initial_identifier,
                widget=autocomplete.ModelSelect2(
                    url=reverse(
                        'catalog:distribution-identifier-autocomplete',
                        kwargs={'node_id': node.id}
                    ),
                    attrs={'class': 'form-control form-control-select-two'}
                )
            )
        self.fields['file_name'].initial = self.instance.file_name
