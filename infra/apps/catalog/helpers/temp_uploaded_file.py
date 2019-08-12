import os

from django.core.files.uploadedfile import TemporaryUploadedFile


def temp_uploaded_file(file):
    file_size = os.path.getsize(file.name)
    file_content = file.read()
    temp = TemporaryUploadedFile(file.name, 'text', file_size, None)
    temp.write(file_content)
    temp.seek(0)
    return temp
