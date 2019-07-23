def file_name_for_format(catalog):
    names = {
        'json': 'data',
        'xlsx': 'catalog'
    }
    file_name = names[catalog.format]
    return file_name
