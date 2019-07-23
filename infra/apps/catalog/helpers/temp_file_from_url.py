from tempfile import NamedTemporaryFile

import requests


def temp_file_from_url(url):
    response = requests.get(url)
    response.raise_for_status()

    file_content = response.content
    fd = NamedTemporaryFile()
    fd.write(file_content)
    fd.seek(0)
    return fd
