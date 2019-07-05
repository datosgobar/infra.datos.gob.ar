# infra.datos.gob.ar

## Setup

### Dependencias

El proyecto es principalmente una aplicación Django, en Python 3.7. Se recomienda usar `pyenv` para instalar Python 3.7.

1. Usar [pyenv-installer](https://github.com/pyenv/pyenv-installer) para instalar `pyenv`, y visitar 
[esta documentación](https://github.com/pyenv/pyenv/wiki/Common-build-problems) para obtener información 
sobre posibles errores.
1. Instalar python 3.7: `pyenv install 3.7.3` (3.7 o mayor)


Usamos [nodejs](https://nodejs.org/en/) para `eslint` y `jscpd`.

1. Instalar `nodejs`, recomendado usar [nvm](https://github.com/creationix/nvm).
1. Instalar `nodejs` versión `10` (stable)
1. Instalar dependencias: `npm install`

Docker y docker-compose son usados para levantar la base de datos.

## Desarrollo local

1. Crear nuevo entorno virtual: `pyenv virtualenv 3.7.3 infra`
1. Crear el archivo`.python-version`: `echo "infra" > .python-version`
1. Instalar dependencias: `pip install -r requirements/local.txt`
1. Levantar servicios (db): `docker-compose up`
1. Correr migraciones: `./manage.py migrate`
1. Crear un superusuario de Django: `./manage.py createsuperuser`


## Tips:

## Levantar el servidor local

* `./manage.py runserver`

## Levantar una shell de Django

* `./manage.py shell`

## Correr tests

* `scripts/tests.sh`

## Run linters de estilo de código


* [Flake8](http://flake8.pycqa.org/en/latest/index.html): `scripts/flake8.sh`
* [Pylint](https://pylint.readthedocs.io/en/latest/): `scripts/pylint.sh`
* [Jscpd](https://github.com/kucherenko/jscpd): `scripts/jscpd.sh`
* [Eslint](https://eslint.org/): `scripts/eslint.sh`
