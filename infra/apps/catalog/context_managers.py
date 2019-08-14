import os
from contextlib import contextmanager

from django.conf import settings


@contextmanager
def distribution_file_handler(same_day_version, new_file_name):
    try:
        file_path_without_date = os.path.join(settings.MEDIA_ROOT, same_day_version.file_path())
        file_path_with_date = \
            os.path.join(settings.MEDIA_ROOT, same_day_version.file_path(with_date=True))
        yield
        if new_file_name != same_day_version.file_name:
            os.remove(file_path_without_date)
            os.remove(file_path_with_date)
    except AttributeError:
        # No hay versión anterior, por lo que 'same_day_version' es None y 'file_path()' tira error
        yield
