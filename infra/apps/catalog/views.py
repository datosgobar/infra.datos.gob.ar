# coding=utf-8
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView
from requests import RequestException

from infra.apps.catalog.exceptions.catalog_not_uploaded_error import \
    CatalogNotUploadedError
from infra.apps.catalog.exceptions.catalog_sync_error import CatalogSyncError
from infra.apps.catalog.forms import CatalogForm, DistributionForm
from infra.apps.catalog.mixins import UserIsNodeAdminMixin
from infra.apps.catalog.models import CatalogUpload, Node, Distribution
from infra.apps.catalog.sync import sync_catalog
from infra.apps.catalog.validator.url_or_file import URLOrFileValidator


class AddCatalogView(LoginRequiredMixin, UserIsNodeAdminMixin, FormView):
    template_name = "catalogs/add_catalog.html"
    form_class = CatalogForm
    success_url = None

    def post(self, request, *args, **kwargs):
        node_id = self.kwargs.get('node_id')
        self.success_url = reverse_lazy('catalog:upload_success', kwargs={'node_id': node_id})
        form = CatalogForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.form_invalid(form)

        try:
            raw_data = form.cleaned_data
            raw_data['node'] = Node.objects.get(pk=node_id)
            catalog = CatalogUpload.create_from_url_or_file(raw_data)
        except ValidationError as e:
            messages.error(request, e)
            return self.form_invalid(form)

        validation_error_messages = catalog.validate()
        for error_message in validation_error_messages:
            messages.info(request, error_message)
        return self.form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AddCatalogView, self).get_context_data(**kwargs)
        node_id = self.kwargs.get('node_id')
        context['node_id'] = node_id
        context['node_identifier'] = Node.objects.get(id=node_id).identifier
        return context

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class DistributionUpserter(TemplateView):
    model = Distribution
    template_name = 'distributions/distribution_form.html'

    def post_error(self, context):
        return self.render_to_response(context, status=400)

    def _get_node(self, node_id):
        try:
            return Node.objects.get(id=node_id)
        except Node.DoesNotExist:
            raise Http404

    def _valid_form(self, form, request):
        if not form.is_valid():
            return False
        try:
            URLOrFileValidator(form.cleaned_data['url'], form.cleaned_data['file']).validate()
        except ValidationError as e:
            messages.error(request, e)
            return False

        return True

    def validate_file_fields(self, file, url):
        if not file and not url:
            raise ValidationError(
                "Se tiene que ingresar por lo menos un archivo o una URL válida.")
        if file and url:
            raise ValidationError("No se pueden ingresar un archivo y una URL a la vez.")

    def create_from_url(self, request, context, node, form):
        try:
            raw_data = {'dataset_identifier': form.cleaned_data['dataset_identifier'],
                        'file_name': form.cleaned_data['file_name'],
                        'identifier': form.cleaned_data['distribution_identifier'],
                        'node': node,
                        'url': form.cleaned_data['url']}
            self.model.create_from_url(raw_data)
        except RequestException:
            messages.error(request, 'Error descargando la distribución desde la URL especificada')
            return self.post_error(context)

        return self.success_url(node)

    def create_from_file(self, node, form):
        self.model.objects.create(
            node=node,
            identifier=form.cleaned_data['distribution_identifier'],
            file=form.cleaned_data['file'],
            dataset_identifier=form.cleaned_data['dataset_identifier'],
            file_name=form.cleaned_data['file_name']
        )

        return self.success_url(node)

    def success_url(self, node):
        return HttpResponseRedirect(
            reverse('catalog:node_distributions', kwargs={'node_id': node.id}))


class AddDistributionView(DistributionUpserter):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        status = 200
        node = self._get_node(kwargs['node_id'])
        context['node_identifier'] = node.identifier

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
        if not self._valid_form(form, request):
            return self.post_error(context)

        if form.cleaned_data['url']:
            return self.create_from_url(request, context, node, form)

        return self.create_from_file(node, form)


class AddDistributionVersionView(DistributionUpserter):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        dist_id = self.kwargs.get('identifier')
        status = 200
        node = self._get_node(kwargs['node_id'])
        context['node_identifier'] = node.identifier

        try:
            distribution = self.get_last_distribution(dist_id, node)
            context['form'] = DistributionForm(
                node=node,
                instance=distribution,
                initial={'distribution_identifier': distribution.identifier}
            )
        except CatalogNotUploadedError:
            status = 400
            msg = f'No se encontraron catálogos subidos para el nodo: {node.identifier}'
            messages.error(request, msg)
        except self.model.DoesNotExist:
            status = 404
            msg = f'No se encontró la distribución {dist_id} para el nodo: {node.identifier}'
            messages.error(request, msg)

        return self.render_to_response(context, status=status)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        node = self._get_node(kwargs['node_id'])
        dist_id = self.kwargs.get('identifier')
        distribution = self.get_last_distribution(dist_id, node)
        form = DistributionForm(request.POST, request.FILES, node=node, instance=distribution)
        context['form'] = form
        if not self._valid_form(form, request):
            return self.post_error(context)

        if form.cleaned_data['url']:
            return self.create_from_url(request, context, node, form)

        return self.create_from_file(node, form)

    def get_last_distribution(self, dist_id, node):
        distribution = self.model.objects.filter(identifier=dist_id, node=node). \
            order_by('uploaded_at').last()
        if distribution:
            distribution.file = None
            return distribution
        raise self.model.DoesNotExist


class ListDistributions(LoginRequiredMixin, UserIsNodeAdminMixin, ListView):
    model = Distribution
    template_name = "distributions/node_distributions.html"

    def get_queryset(self):
        node = self.kwargs['node_id']
        return self.model.objects.filter(node=node)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListDistributions, self).get_context_data(object_list=object_list, **kwargs)
        context['node'] = Node.objects.get(id=self.kwargs['node_id'])
        context['object_list'] = \
            self.last_three_versions_of_each_distribution(context['object_list'])
        return context

    def last_three_versions_of_each_distribution(self, queryset):
        qs = {}
        for distribution in queryset:
            qs.setdefault(distribution.identifier, []).append(distribution)

        for distributions in qs.values():
            distributions.sort(key=lambda x: (x.uploaded_at, x.id), reverse=True)
            del distributions[3:]
        return qs


class CatalogUploadSuccess(LoginRequiredMixin, UserIsNodeAdminMixin, TemplateView):
    template_name = "catalogs/catalog_success.html"

    def get(self, request, *args, **kwargs):
        node_id = self.kwargs.get('node_id')
        params_dict = {'node_id': node_id,
                       'node_identifier': Node.objects.get(pk=node_id).identifier}
        return render(request, self.template_name, params_dict)


class NodeListView(LoginRequiredMixin, ListView):
    model = Node
    template_name = "nodes/index.html"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Node.objects.all()
        return user.node_set.all()


class NodeUploadsView(LoginRequiredMixin, UserIsNodeAdminMixin, ListView):
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


class DistributionUploads(ListView):
    model = Distribution
    template_name = 'distributions/uploads.html'

    def node_id(self):
        return self.kwargs['node_id']

    def identifier(self):
        return self.kwargs['identifier']

    def get_queryset(self):
        return (self.model.objects
                .filter(node=self.node_id(),
                        identifier=self.identifier())
                .order_by('-uploaded_at'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DistributionUploads, self).get_context_data(object_list=object_list,
                                                                    **kwargs)
        context['identifier'] = self.identifier()
        context['node_id'] = self.node_id()
        context['node_identifier'] = Node.objects.get(id=self.node_id()).identifier
        return context


class SyncCatalog(LoginRequiredMixin, TemplateView):
    template_name = 'catalogs/catalog_success.html'
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return self.handle_no_permission()

        node_id = self.kwargs['node_id']
        try:
            errors = sync_catalog(node_id)
            for error in errors:
                messages.info(request, error)
            status = 200
        except CatalogSyncError as error:
            messages.error(request, error)
            status = 400

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=status)

    def get_context_data(self, **kwargs):
        context = super(SyncCatalog, self).get_context_data(**kwargs)
        context['node_id'] = self.kwargs['node_id']
        context['node_identifier'] = self.id_if_exists()
        return context

    def id_if_exists(self):
        try:
            return Node.objects.get(id=self.kwargs['node_id']).identifier
        except Node.DoesNotExist:
            return None
