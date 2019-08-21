import os

from infra.apps.catalog.constants import CATALOG_ROOT
from infra.apps.catalog.helpers.file_name_for_format import file_name_for_format


def catalog_file_path(instance, file_format, _filename=None):
    file_name = file_name_for_format(file_format)

    return os.path.join(CATALOG_ROOT,
                        instance.node.identifier,
                        f'{file_name}-{instance.uploaded_at}.{file_format}')


def json_catalog_file_path(instance, _filename=None):
    return catalog_file_path(instance, 'json')


def xlsx_catalog_file_path(instance, _filename=None):
    return catalog_file_path(instance, 'xlsx')
