def file_name_for_format(file_format):
    names = {
        'json': 'data',
        'xlsx': 'catalog'
    }
    file_name = names[file_format]
    return file_name
