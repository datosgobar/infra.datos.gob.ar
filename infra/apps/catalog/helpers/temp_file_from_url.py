import requests
import tempfile


def temp_file_from_url(url):
    response = requests.get(url)
    response.raise_for_status()

    file_content = response.content
    name = response.url.rsplit('/', maxsplit=1)[-1]
    fd = open(f'/{tempfile.gettempdir()}/{name}', 'wb+')
    fd.write(file_content)
    fd.seek(0)
    return fd
