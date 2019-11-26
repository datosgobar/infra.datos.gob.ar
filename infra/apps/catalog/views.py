# coding=utf-8
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView, DeleteView
from requests import RequestException

from infra.apps.catalog.exceptions.catalog_not_uploaded_error import \
    CatalogNotUploadedError
from infra.apps.catalog.exceptions.catalog_sync_error import CatalogSyncError
from infra.apps.catalog.forms import CatalogForm, DistributionForm
from infra.apps.catalog.mixins import UserIsNodeAdminMixin
from infra.apps.catalog.models import CatalogUpload, Node, DistributionUpload
from infra.apps.catalog.models.distribution import Distribution
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

    def generate_distribution(self, form, node, request, context):
        try:
            data = form.cleaned_data
            self.model.objects.upsert_upload(node, data)
        except RequestException:
            messages.error(request, 'Error descargando la distribución desde la URL especificada')
            return self.post_error(context)

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

        return self.generate_distribution(form, node, request, context)


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

        return self.generate_distribution(form, node, request, context)

    def get_last_distribution(self, dist_id, node):
        distribution = self.model.objects.filter(identifier=dist_id, catalog=node).first()
        if distribution:
            distribution.file = None
            return distribution
        raise self.model.DoesNotExist


class ListDistributions(LoginRequiredMixin, UserIsNodeAdminMixin, ListView):
    model = DistributionUpload
    paginate_by = 10
    template_name = "distributions/node_distributions.html"

    # pylint: disable=W0201
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data(**kwargs)
        selected_dataset = request.GET.get('dataset_identifier', None)

        if not selected_dataset:
            return self.render_to_response(context)

        distributions = {id: dist for id, dist in context.get('object_list').items()
                         if dist[0].distribution.dataset_identifier == selected_dataset}

        context.update({
            'object_list': distributions,
            'selected_dataset': selected_dataset,
        })

        return self.render_to_response(context)

    def get_queryset(self):
        node = self.kwargs['node_id']
        return self.model.objects.filter(distribution__catalog=node)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListDistributions, self).get_context_data(object_list=object_list, **kwargs)
        context['node'] = Node.objects.get(id=self.kwargs['node_id'])
        context['object_list'] = \
            self.last_three_versions_of_each_distribution(context['object_list'])

        datasets = []
        for _, dist in context.get('object_list').items():
            datasets.append(self._get_dataset_id_title_pair(dist))
        datasets = list(set(datasets))
        context['dataset_list'] = datasets
        return context

    def last_three_versions_of_each_distribution(self, queryset):
        qs = {}
        for upload in queryset:
            qs.setdefault(upload.distribution.identifier, []).append(upload)

        for distributions in qs.values():
            distributions.sort(key=lambda x: (x.uploaded_at, x.id), reverse=True)
        return qs

    def _get_dataset_id_title_pair(self, distributions):
        distribution = distributions[0].distribution
        latest_catalog_upload = distribution.catalog.get_latest_catalog_upload()
        pair = None
        for dataset in latest_catalog_upload.get_datasets():
            if dataset['identifier'] == distribution.dataset_identifier:
                pair = (dataset['identifier'], dataset['title'] + " - " + dataset['identifier'])

        return pair


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
        base_path = os.path.join(settings.MEDIA_ROOT, settings.CATALOG_MEDIA_DIR)
        has_json = os.path.isfile(os.path.join(base_path, node_name, 'data.json'))
        has_xlsx = os.path.isfile(os.path.join(base_path, node_name, 'catalog.xlsx'))
        params_dict = {
            'node_id': node_id,
            'base_url': f'{settings.MEDIA_URL}catalog/',
            'node_name': node_name,
            'has_json': has_json,
            'has_xlsx': has_xlsx,
            'object_list': node_uploads
        }
        return render(request, self.template_name, params_dict)


class DistributionUploads(LoginRequiredMixin, UserIsNodeAdminMixin, ListView):
    model = DistributionUpload
    template_name = 'distributions/distribution_history.html'
    paginate_by = 10

    def node_id(self):
        return self.kwargs['node_id']

    def identifier(self):
        return self.kwargs['identifier']

    def get_queryset(self):
        return (self.model.objects
                .filter(distribution__catalog=self.node_id(),
                        distribution__identifier=self.identifier())
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


class CatalogHistory(LoginRequiredMixin, UserIsNodeAdminMixin, ListView):
    model = CatalogUpload
    template_name = 'catalogs/catalog_history.html'
    http_method_names = ['get']

    def get_queryset(self):
        node = self.kwargs["node_id"]
        return self.model.objects.filter(node=node).order_by("-uploaded_at")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CatalogHistory, self).get_context_data(object_list=object_list, **kwargs)
        context['node'] = Node.objects.get(id=self.kwargs['node_id'])
        return context


class DeleteCatalogUpload(LoginRequiredMixin, UserIsNodeAdminMixin, DeleteView):
    model = CatalogUpload
    http_method_names = ['post']

    def get_success_url(self):
        return reverse_lazy('catalog:catalog_history',
                            kwargs={'node_id': self.kwargs["node_id"]})

    def delete(self, request, *args, **kwargs):
        catalog = self.get_object()
        if catalog.node.id != self.kwargs["node_id"]:
            return HttpResponse('Unauthorized', status=401)
        success_url = self.get_success_url()
        catalog.delete()
        return HttpResponseRedirect(success_url)


class DeleteDistribution(LoginRequiredMixin, UserIsNodeAdminMixin, View):

    def post(self, request, node_id, identifier):
        get_object_or_404(Distribution, identifier=identifier, catalog=node_id).delete()
        return redirect('catalog:distribution_uploads',
                        node_id=node_id, identifier=identifier)


class DeleteDistributionUpload(LoginRequiredMixin, UserIsNodeAdminMixin, DeleteView):
    model = DistributionUpload
    http_method_names = ['post']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.distribution_upload = None

    def get_success_url(self):
        if self.distribution_upload.distribution.distributionupload_set.count() > 1:
            return reverse_lazy('catalog:distribution_uploads',
                                kwargs={
                                    'node_id': self.kwargs["node_id"],
                                    'identifier': self.distribution_upload.distribution.identifier
                                })
        return reverse_lazy('catalog:node_distributions',
                            kwargs={
                                'node_id': self.kwargs["node_id"],
                            })

    def delete(self, request, *args, **kwargs):
        self.distribution_upload = self.get_object()
        if self.distribution_upload.distribution.catalog.id != self.kwargs["node_id"]:
            return HttpResponse('Unauthorized', status=401)
        success_url = self.get_success_url()
        dist = self.distribution_upload.distribution
        self.distribution_upload.delete()
        if not dist.distributionupload_set.count():
            dist.delete()
        return HttpResponseRedirect(success_url)
