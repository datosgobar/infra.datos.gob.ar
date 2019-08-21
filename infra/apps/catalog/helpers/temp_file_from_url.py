import os
import tempfile

import requests


def temp_file_from_url(url):
    response = requests.get(url)
    response.raise_for_status()

    file_content = response.content
    name = os.path.basename(response.url)
    if not name:
        name = response.url.rsplit('/')[-2]
    fd = open(f'/{tempfile.gettempdir()}/{name}', 'wb+')
    fd.write(file_content)
    fd.seek(0)
    return fd
