import os

from django.conf import settings
from pydatajson import DataJson
from pydatajson.writers import write_xlsx_catalog, write_json_catalog

from infra.apps.catalog.models.catalog_upload import json_catalog_file_path, xlsx_catalog_file_path


def create_new_file(instance):
    get_existing_file_path = json_catalog_file_path if instance.json_file \
                else xlsx_catalog_file_path
    get_new_file_path = xlsx_catalog_file_path if instance.json_file \
        else json_catalog_file_path
    write_new_file = write_xlsx_catalog if instance.json_file else write_json_catalog

    data = DataJson(os.path.join(settings.MEDIA_ROOT, get_existing_file_path(instance)))
    path = os.path.join(settings.MEDIA_ROOT, get_new_file_path(instance))
    write_new_file(data, path)
    return path