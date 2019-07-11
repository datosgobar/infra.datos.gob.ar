import errno
import json
import os
from urllib import request as urllib_request
from urllib.error import HTTPError

from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.views.generic import ListView
from django.views.generic.edit import FormView
from pydatajson import DataJson

from infra.apps.catalog.forms import CatalogForm
from infra.apps.catalog.models import Catalog

from django.conf import settings


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

    def form_valid(self, form):
        file_format = form.cleaned_data['format']
        # TODO: Crear tmp_file para manipular tanto en el caso de archivo o URL, y pasar ese tmp_file
        #  como parametro de DataJson

        if form.cleaned_data['file']:
            file_to_upload = form.cleaned_data['file']
            identifier = json.loads(file_to_upload.read())['identifier']
        else:
            # Download the file contents from the specified URL
            try:
                file_content = urllib_request.urlopen(form.cleaned_data['url']).read()
            except HTTPError as e:
                raise ConnectionError(f'No se pudo conectar a la URL ingresada: {e}')


            # TODO: validar que el response sea 200, no sea còdigo HTML, y que haya identifier
            identifier = DataJson(form.cleaned_data['url'])['identifier']


            path = f'{settings.MEDIA_ROOT}/catalogs/{identifier}/data.{file_format}'

            if not os.path.exists(os.path.dirname(path)):
                try:
                    os.makedirs(os.path.dirname(path))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise OSError("Hubo un problema con el guardado del archivo del catálogo.")

            final_file = open(path, 'ab+')
            final_file.write(file_content)
            file_to_upload = File(file=final_file)

        Catalog.objects.create(
            identifier=identifier,
            format=form.cleaned_data['format'],
            file=file_to_upload
        )

        if not file_to_upload.closed:
            file_to_upload.close()

        return super().form_valid(form)
