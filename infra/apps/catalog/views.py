# coding=utf-8

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
        if form.is_valid():
            return self.form_valid(form)
        return self.render_to_response(self.get_context_data(form=form), status=400)

    def form_valid(self, form):
        data = CatalogDataValidator().get_and_validate_data(form.cleaned_data)

        Catalog.objects.create(**data)

        if not data.get('file').closed:
            data.get('file').close()

        return super().form_valid(form)
