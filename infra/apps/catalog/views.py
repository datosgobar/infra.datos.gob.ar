# coding=utf-8
import os
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView
from requests import RequestException

from infra.apps.catalog.exceptions.catalog_not_uploaded_error import CatalogNotUploadedError
from infra.apps.catalog.forms import CatalogForm, DistributionForm
from infra.apps.catalog.mixins import UserIsNodeAdminMixin
from infra.apps.catalog.models import CatalogUpload, Node, Distribution
from infra.apps.catalog.validator.url_or_file import URLOrFileValidator


class CatalogView(ListView):
    model = CatalogUpload
    template_name = "index.html"

    def get_queryset(self):
        nodes = self.request.user.node_set.all()
        return CatalogUpload.objects.filter(node__in=nodes)


class AddCatalogView(FormView):
    template_name = "add.html"
    form_class = CatalogForm
    success_url = reverse_lazy('catalog:upload_success')

    def get_form_kwargs(self):
        kwargs = super(AddCatalogView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        form = CatalogForm(request.POST, request.FILES, user=self.request.user)
        if not form.is_valid():
            return self.form_invalid(form)

        try:
            catalog = CatalogUpload.create_from_url_or_file(form.cleaned_data)
        except ValidationError as e:
            messages.error(request, e)
            return self.form_invalid(form)

        validation_error_messages = catalog.validate()
        for error_message in validation_error_messages:
            messages.info(request, error_message)
        return self.form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class AddDistribution(UserIsNodeAdminMixin, TemplateView):
    template_name = 'add_distribution.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        status = 200
        node = self._get_node(kwargs['node_id'])

        try:
            context['form'] = DistributionForm(node=node)
        except CatalogNotUploadedError:
            status = 400
            msg = f'No se encontraron catálogos subidos para el nodo: {node.identifier}'
            messages.error(request, msg)

        return self.render_to_response(context, status=status)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        node = self._get_node(kwargs['node_id'])
        form = DistributionForm(request.POST, request.FILES, node=node)
        context['form'] = form
        if not self._valid_form(form):
            return self.post_error(context)

        if form.cleaned_data['url']:
            return self.create_from_url(request, context, node, form)

        return self.create_from_file(node, form)

    def post_error(self, context):
        return self.render_to_response(context, status=400)

    def _get_node(self, node_id):
        try:
            return Node.objects.get(id=node_id)
        except Node.DoesNotExist:
            raise Http404

    def _valid_form(self, form):
        if not form.is_valid():
            return False
        try:
            URLOrFileValidator(form.cleaned_data['url'], form.cleaned_data['file']).validate()
        except ValidationError:
            return False

        return True

    def create_from_url(self, request, context, node, form):
        try:
            Distribution.create_from_url(form.cleaned_data['url'],
                                         node,
                                         form.cleaned_data['dataset_identifier'],
                                         form.cleaned_data['distribution_identifier'])
        except RequestException:
            messages.error(request, 'Error descargando la distribución desde la URL especificada')
            return self.post_error(context)

        return self.success_url(node)

    def create_from_file(self, node, form):
        Distribution.objects.create(node=node,
                                    file=form.cleaned_data['file'],
                                    dataset_identifier=form.cleaned_data['dataset_identifier'],
                                    identifier=form.cleaned_data['distribution_identifier'])

        return self.success_url(node)

    def success_url(self, node):
        return HttpResponseRedirect(reverse('catalog:node_catalogs',
                                            kwargs={'node_id': node.id}))


class ListDistributions(UserIsNodeAdminMixin, ListView):
    model = Distribution
    template_name = "list_distributions.html"

    def get_queryset(self):
        node = self.kwargs['node_id']
        return self.model.objects.filter(node=node)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListDistributions, self).get_context_data(object_list=object_list, **kwargs)
        context['node'] = Node.objects.get(id=self.kwargs['node_id'])
        return context


class CatalogUploadSuccess(TemplateView):
    template_name = "catalog_success.html"


class NodeListView(ListView):
    model = Node
    template_name = "nodes/index.html"

    def get_queryset(self):
        user = self.request.user
        return user.node_set.all()


class NodeUploadsView(UserIsNodeAdminMixin, ListView):
    model = CatalogUpload
    template_name = "nodes/uploads.html"

    def get(self, request, *args, **kwargs):
        node_id = self.kwargs['node_id']
        node_name = Node.objects.get(pk=node_id).identifier
        node_uploads = self.model.objects.filter(node=node_id).order_by('-uploaded_at')
        base_url = settings.CATALOG_SERVING_URL
        has_xlsx = os.path.isfile(os.path.join(base_url, node_name, 'catalog.xlsx')[1:])
        params_dict = {
            'node_id': node_id,
            'base_url': base_url,
            'node_name': node_name,
            'has_xlsx': has_xlsx,
            'object_list': node_uploads
        }
        return render(request, self.template_name, params_dict)
