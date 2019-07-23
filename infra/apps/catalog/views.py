# coding=utf-8
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView

from infra.apps.catalog.exceptions.catalog_not_uploaded_error import CatalogNotUploadedError
from infra.apps.catalog.forms import CatalogForm, DistributionForm
from infra.apps.catalog.models import CatalogUpload, Node


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
        except ValidationError as e:
            messages.error(request, e)
            return self.form_invalid(form)

        return self.form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class AddDistribution(TemplateView):
    template_name = 'add_distribution.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        status = 200
        try:
            node = Node.objects.get(id=kwargs['node'])
        except Node.DoesNotExist:
            raise Http404

        try:
            context['form'] = DistributionForm(node)
        except CatalogNotUploadedError:
            status = 400
            messages.error(request, f'No se encontraron catálogos subidos para el nodo: {node.identifier}')

        return self.render_to_response(context, status=status)
