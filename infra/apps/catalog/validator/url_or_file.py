from django.core.exceptions import ValidationError


class URLOrFileValidator:
    def __init__(self, url, file):
        self.url = url
        self.file = file

    def validate(self):
        if not self.file and not self.url:
            raise ValidationError("Se tiene que ingresar por lo menos un archivo o una URL válida.")
        if self.file and self.url:
            raise ValidationError("No se pueden ingresar un archivo y una URL a la vez.")
