def file_name_for_format(format):
    names = {
        'json': 'data',
        'xlsx': 'catalog'
    }
    file_name = names[format]
    return file_name
