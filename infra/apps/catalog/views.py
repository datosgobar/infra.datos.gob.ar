# coding=utf-8
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import FormView
from pydatajson import DataJson
from pydatajson.readers import read_catalog
from django.conf import settings

from infra.apps.catalog.forms import CatalogForm
from infra.apps.catalog.models import CatalogUpload


class CatalogView(ListView):
    model = CatalogUpload
    template_name = "index.html"


class AddCatalogView(FormView):
    template_name = "add.html"
    form_class = CatalogForm
    success_url = reverse_lazy('catalog:list')

    def post(self, request, *args, **kwargs):
        form = CatalogForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.form_invalid(form)

        try:
            CatalogUpload.create_from_url_or_file(form.cleaned_data)
            catalog = CatalogUpload.create_from_url_or_file(form.cleaned_data)
        except ValidationError as e:
            messages.error(request, e)
            return self.form_invalid(form)

        catalog_file_path = 'media/' + catalog.file.name
        catalog_content = read_catalog(catalog_file_path)

        dj = DataJson()

        if not dj.is_valid_catalog(catalog_content):
            catalog.delete()
            error_report = dj.validate_catalog(catalog_content)
            errors = error_report['error']['catalog']['errors']
            error_messages = '. '.join([error['message'] for error in errors])
            messages.error(request, "El catálogo ingresado no es valido: " + error_messages)

            return self.form_invalid(form)

        return self.form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response
