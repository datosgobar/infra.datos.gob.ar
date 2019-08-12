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
        super(DistributionForm, self).__init__(*args, **kwargs)
        self.fields['dataset_identifier'] = \
            autocomplete.Select2ListChoiceField(
                widget=autocomplete.ListSelect2(
                    url=reverse(
                        'catalog:distribution-identifier-autocomplete',
                        kwargs={'node_id': node.id}
                    ),
                    attrs={'class': 'form-control form-control-select-two'}
                )
            )
        self.fields['file_name'].initial = self.instance.file_name
