# coding=utf-8
import logging
from django.core.exceptions import ValidationError
from django.core.files import File
from pydatajson import DataJson
from pydatajson.custom_exceptions import NonParseableCatalog
from requests import RequestException

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

        file_field = 'json_file' if file_format == 'json' else 'xlsx_file'

        return {'node': raw_data['node'], 'format': file_format, file_field: File(file_handler)}

    def validate_format(self, url, file, _format):
        path = file.temporary_file_path() if file else url
        try:
            DataJson(path, catalog_format=_format)
        except NonParseableCatalog:
            raise ValidationError("El catálogo ingresado no es válido")
        except Exception as e:
            logging.getLogger(__file__).error(e)
            raise ValidationError("El catálogo ingresado no es válido")

    def download_file_from_url(self, url):
        try:
            return temp_file_from_url(url)
        except RequestException:
            raise ValidationError('Error descargando el catálogo de la URL especificada')
