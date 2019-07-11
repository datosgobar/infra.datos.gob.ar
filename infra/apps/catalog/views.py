import errno
import os
import uuid
from urllib import request as urllib_request
from urllib.error import HTTPError

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.views.generic import ListView
from django.views.generic.edit import FormView
from pydatajson import DataJson

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
        return self.render_to_response(self.get_context_data(form=form))

    def generate_form_data(self, form):
        file_format = form.cleaned_data['format']

        if form.cleaned_data['file']:
            temp_file = NamedTemporaryFile(dir='/tmp', prefix=str(uuid.uuid4()))
            file_to_upload = form.cleaned_data['file']
            temp_file.write(file_to_upload.read())
            identifier = DataJson(temp_file.name).get('identifier')
            temp_file.close()
            if not identifier:
                raise ValidationError('El catálogo subido no posee el campo "identifier"')
        else:
            # Download the file contents from the specified URL
            try:
                file_content = urllib_request.urlopen(form.cleaned_data['url']).read()
            except HTTPError as error:
                raise ConnectionError(f'No se pudo conectar a la URL ingresada: {error}')

            identifier = DataJson(form.cleaned_data['url'])['identifier']
            if not identifier:
                raise ValidationError('El catálogo indicado no posee el campo "identifier"')

            path = f'{settings.MEDIA_ROOT}/catalogs/{identifier}/data.{file_format}'

            if not os.path.exists(os.path.dirname(path)):
                try:
                    os.makedirs(os.path.dirname(path))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise OSError("Hubo un problema con el guardado del archivo del catálogo.")

            final_file = open(path, 'ab+')
            final_file.write(file_content)
            file_to_upload = File(file=final_file)

        return identifier, file_format, file_to_upload

    def form_valid(self, form):

        identifier, file_format, file_to_upload = self.generate_form_data(form)

        Catalog.objects.create(
            identifier=identifier,
            format=file_format,
            file=file_to_upload
        )

        if not file_to_upload.closed:
            file_to_upload.close()

        return super().form_valid(form)
