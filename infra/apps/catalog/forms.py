# coding=utf-8
from django import forms
from django.core.exceptions import ValidationError

from infra.apps.catalog.models import CatalogUpload, Node

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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CatalogForm, self).__init__(*args, **kwargs)
        if not self.user.is_superuser:
            self.fields['node'] = forms.ChoiceField(required=True)
            self.fields['node'].choices = self.get_user_nodes()

    def get_user_nodes(self):
        nodes = self.user.node_set.all()
        return [(node.identifier, node.identifier) for node in nodes]

    def clean_node(self):
        try:
            node = Node.objects.get(identifier=self.cleaned_data['node'])
        except Node.DoesNotExist:
            raise ValidationError('No existe nodo con ese identifier')
        if self.user not in node.admins.all():
            raise ValidationError('El usuario no es administrador del nodo')
        return node


class DistributionForm(forms.Form):

    file = forms.FileField(required=False)
    url = forms.URLField(required=False)
    distribution_identifier = forms.CharField()

    def __init__(self, *args, **kwargs):
        node = kwargs.pop('node')
        super(DistributionForm, self).__init__(*args, **kwargs)
        latest = node.get_latest_catalog_upload()
        datasets = [(x['identifier'], x['identifier']) for x in latest.get_datasets()]
        self.fields['dataset_identifier'] = forms.ChoiceField(choices=datasets)
