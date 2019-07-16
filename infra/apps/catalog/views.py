# coding=utf-8
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.generic import ListView
from django.views.generic.edit import FormView

from infra.apps.catalog.catalog_data_validator import CatalogDataValidator
from infra.apps.catalog.forms import CatalogForm
from infra.apps.catalog.models import Catalog


class CatalogView(ListView):
    model = Catalog
    template_name = "index.html"


class AddCatalogView(FormView):
    template_name = "add.html"
    form_class = CatalogForm
    success_url = '/catalogs/'

    def post(self, request, *args, **kwargs):
        form = CatalogForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.form_invalid(form)

        try:
            data = CatalogDataValidator().get_and_validate_data(form.cleaned_data)
        except ValidationError as e:
            messages.error(request, e)
            return self.form_invalid(form)

        Catalog.objects.create(**data)

        if not data.get('file').closed:
            data.get('file').close()
        return self.form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response
