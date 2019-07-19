# coding=utf-8
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import FormView
from pydatajson import DataJson

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
            catalog = CatalogUpload.create_from_url_or_file(form.cleaned_data)
        except ValidationError as e:
            messages.error(request, e)
            return self.form_invalid(form)

        return self.validate_catalog(request, form, catalog)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response

    def validate_catalog(self, request,  form, catalog):
        catalog_file_path = settings.MEDIA_ROOT + '/' + catalog.file.name

        try:
            dj = DataJson(catalog_file_path)
        except KeyError:
            catalog.delete()
            messages.error(request, "No se puede validar el catálogo ingresado")
            return self.form_invalid(form)

        if not dj.is_valid_catalog():
            catalog.delete()
            error_report = dj.validate_catalog()
            errors = error_report['error']['catalog']['errors']

            for dataset in error_report['error']['dataset']:
                errors += dataset['errors']

            error_messages = '. '.join([error['message'] for error in errors])
            messages.error(request, "El catálogo ingresado no es valido: " + error_messages)
            return self.form_invalid(form)

        return self.form_valid(form)
