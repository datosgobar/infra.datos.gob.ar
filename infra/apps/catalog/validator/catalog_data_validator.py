# coding=utf-8
from requests import RequestException
from django.core.exceptions import ValidationError
from django.core.files import File

from infra.apps.catalog.helpers.temp_file_from_url import temp_file_from_url
from infra.apps.catalog.validator.url_or_file import URLOrFileValidator


class CatalogDataValidator:
    def get_and_validate_data(self, raw_data):
        file_handler = raw_data.get('file')
        file_format = raw_data.get('format')
        url = raw_data.get('url')

        URLOrFileValidator(file_handler, url).validate()
        self.validate_format(url, file_handler, file_format)

        if url:
            file_handler = self.download_file_from_url(url)

        return {'node': raw_data['node'], 'format': file_format, 'file': File(file_handler)}

    def validate_format(self, url, file, _format):
        file_format = (url or file.name).split('.')[-1]
        if len(file_format) > 4:
            file_format = (url or file.name).split("format=")[1][:4]
        if file_format != _format:
            raise ValidationError("El formato ingresado no coincide con el del archivo.")
        return file_format

    def download_file_from_url(self, url):
        try:
            return temp_file_from_url(url)
        except RequestException:
            raise ValidationError('Error descargando el catálogo de la URL especificada')
