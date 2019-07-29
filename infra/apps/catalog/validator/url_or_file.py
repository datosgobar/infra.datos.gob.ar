from django.core.exceptions import ValidationError


class URLOrFileValidator:
    def __init__(self, url, file, editing=False, clear_file=False):
        self.url = url
        self.file = file
        self.editing = editing
        self.clear_file = clear_file

    def validate(self):
        if not self.file and not self.url and (self.editing and self.clear_file):
            raise ValidationError("Se tiene que ingresar por lo menos un archivo o una URL válida.")
        if self.file and self.url:
            raise ValidationError("No se pueden ingresar un archivo y una URL a la vez.")
