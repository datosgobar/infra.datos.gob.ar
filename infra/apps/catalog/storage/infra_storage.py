import os

from django.core.files.storage import FileSystemStorage


class InfraStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
        return name

    def save_as_latest(self, instance):
        path = self.latest_file_path(instance)
        self.save(path, instance.file)
        instance.file.seek(0)

    def latest_file_path(self, instance):
        raise NotImplementedError
