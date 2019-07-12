# coding=utf-8
import requests
from requests import RequestException
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile


class CatalogDataValidator:
    def get_and_validate_data(self, raw_data):
        file_handler = raw_data.get('file')
        file_format = raw_data.get('format')
        identifier = raw_data.get('identifier')
        url = raw_data.get('url')

        self.validate_file_and_url_fields(file_handler, file_format, url)

        if url:
            # Download the file contents from the specified URL
            file_handler = self.download_file_from_url(url)

        return {'identifier': identifier, 'format': file_format, 'file': File(file_handler)}

    def download_file_from_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except RequestException:
            raise ValidationError('Error descargando el catálogo de la URL especificada')

        file_content = response.content
        fd = NamedTemporaryFile()
        fd.write(file_content)
        fd.seek(0)
        return fd

    def validate_file_and_url_fields(self, form_file, form_format, form_url):
        if not form_file and not form_url:
            raise ValidationError("Se tiene que ingresar por lo menos un archivo o una URL válida.")
        if form_file and form_url:
            raise ValidationError("No se pueden ingresar un archivo y una URL a la vez.")
        file_format = (form_url or form_file.name).split('.')[-1]
        if file_format != form_format:
            raise ValidationError("El formato ingresado no coincide con el del archivo.")