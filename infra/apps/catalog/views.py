# coding=utf-8
import os

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import FormView

from infra.apps.catalog.forms import CatalogForm
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


class NodeListView(ListView):
    model = Node
    template_name = "nodes/index.html"


class NodeUploadsView(ListView):
    model = CatalogUpload
    template_name = "nodes/uploads.html"

    def get(self, request, *args, **kwargs):
        node_id = self.kwargs['id']
        node_name = Node.objects.get(pk=node_id).identifier
        node_uploads = self.model.objects.filter(node=node_id).order_by('-uploaded_at')
        base_url = settings.CATALOG_SERVING_URL
        has_xlsx = os.path.isfile(os.path.join(base_url, node_name, 'catalog.xlsx')[1:])
        params_dict = {
            'base_url': base_url,
            'node_name': node_name,
            'has_xlsx': has_xlsx,
            'object_list': node_uploads
        }
        return render(request, self.template_name, params_dict)
