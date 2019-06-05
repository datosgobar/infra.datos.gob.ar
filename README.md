# infra.datos.gob.ar
Sistema de almacenamiento de archivos y catálogos de infra.datos.gob.ar.

## Usos

Permite otorgar usuarios nominales a referentes técnicos de la Red de Nodos de Datos Abiertos de la Administración Pública Nacional para que puedan almacenar archivos de datos abiertos y catálogos de datos abiertos en https://infra.datos.gob.ar.

Un usuario común (no admin) puede loggearse en **https://infra.datos.gob.ar/admin** y tener (o no) permisos para las siguientes acciones:

* Cargar o pisar la versión actual (o por primera vez) de un **catálogo en XLSX o JSON (permiso catálogo)**.
* Cargar o pisar la versión actual (o por primera vez) de una **distribución (permiso distribución)**.

## Permisos

Los usuarios son creados por el equipo de Datos Argentina a pedido de los referentes de los nodos publicadores.

* Se pueden crear usuarios que tengan permiso **sólo para cargar o pisar catálogos**.
* Se pueden crear usuarios que tengan permiso **sólo para cargar o pisar distribuciones**.
* Se pueden crear usuarios que tengan permiso para **cargar o pisar catálogos o distribuciones**.
* Un determinado usuario (no admin) **sólo puede actuar dentro de un nodo determinado**, no puede cargar o pisar catálogos o distribuciones de un nodo distinto al que está asociado.

## Cargar archivos de datos

El usuario dispone de un formulario en el admin de Django que le solicita seleccionar de una lista:

* **Dataset** al que pertenece el archivo que se quiere cargar (si el dataset no existe, le solicita el identificador que el dataset tendrá).
* **Distribución** a la que pertenece el archivo que se quiere cargar (si la distribución no existe, le solicita el identificador que la distribución tendrá).
* **UPLOAD** del archivo asociado a ese dataset y distribución.

**Nota**: el formulario muestra también a qué catálogo se estará cargando el archivo, pero no permite modificarlo.

Una vez subido, validado y guardado, el formulario muestra la URL de descarga generada desde donde se puede descargar el archivo:

https://infra.datos.gob.ar/catalog/{catalog_id}/dataset/{dataset_id}/distribution/{distribution_id}/download/nombre-archivo.csv

### Validaciones

* Si la distribución existe en el catálogo
    - Se valida que el nombre del archivo coincida con `distribution_fileName`. Si no coincide lo rechaza e imprime el motivo del error.
* Si la distribución no existe en el catálogo
    - La primera vez que se carga: se almacena internamente el nombre del archivo.
    - Si ya se cargó el archivo por primera vez: se chequea que el nombre del nuevo archivo sea idéntico al anteriormente guardado. Si no lo es, pide una confirmación antes de proceder con el cambio de nombre.

### Versionado de archivos

Los archivos pisados reemplazan el contenido al que se puede acceder en https://infra.datos.gob.ar/catalog/{catalog_id}/dataset/{dataset_id}/distribution/{distribution_id}/download/nombre-archivo.csv y a su vez generan una copia fechada en https://infra.datos.gob.ar/catalog/{catalog_id}/dataset/{dataset_id}/distribution/{distribution_id}/download/nombre-archivo-{iso_date}.csv donde `iso_date` adopta la forma `YYYY-MM-DD` de la fecha en que se carga el archivo.

De esta manera, el sistema genera un versionado de los archivos cargados anteriormente que se mantiene accesible en caso de conocer la fecha de carga, pero la ruta con el nombre normal del archivo se mantiene invariante.

### FTP

El mismo usuario y contraseña nominal que permiten acceder por interfaz web y cargar un archivo, permiten cargar un archivo en la ruta `/dataset/{dataset_id}/distribution/{distribution_id}/download/nombre-archivo-{iso_date}.csv` por FTP.

**En ningún caso, un usuario puede cargar archivos a un catálogo al cual no esté asociado y tenga permisos**.

### API

El proyecto infra.datos.gob.ar cuenta con una API que permite programáticamente subir archivos de datos mediante el protocolo HTTP. Todos los recursos de la API requieren un *token* de autenticación, el cual puede ser generado por usuarios ya existentes del proyecto mediante la interfaz web.

Los recursos de la API son:

#### Subir archivo (`/api/upload-file`)
**Request:**
- URL: https://infra.datos.gob.ar/api/upload-file
- Método: **POST**
- Headers:
    - `Authorization`: Debe tomar el valor "Bearer " seguido del token.
- Parámetros (Querystring):
    - `catalog` **(requerido)**: ID del catálogo.
    - `dataset` **(requerido)**: ID del dataset.
    - `distribution` **(requerido)**: ID de la distribucion.
    - `name` **(requerido)**: Nombre del archivo.
    - `force`: Cuando está presente, permite establecer un nuevo nombre de archivo para una distribución que ya cuenta con un archivo.
- Body: Contenido del archivo sin procesar **(requerido)**.

Ejemplo:
```
curl -X POST https://infra.datos.gob.ar/api/upload-file?catalog=1&dataset=10&distribution=test&name=values.csv \
     --header "Authorization: Bearer <TOKEN>" \
     --header "Content-Type: application/octet-stream" \
     --data-binary @values.csv
```

**Response: 200 OK**
```json
{
    "url": "https://infra.datos.gob.ar/catalog/1/dataset/10/distribution/test/download/values.csv",
	"replaced": false
}
```

**Response: 400 Bad Request**
```json
{
	"error": {
		"code": 1000,
		"message": "La distribución ya cuenta con un archivo con nombre distinto."
	}
}
```

**Response: 403 Unauthorized**
```json
{
	"error": {
		"code": 1001,
		"message": "No se cuenta con los permisos necesarios para crear el archivo."
	}
}
```

## Cargar catálogos

El usuario dispone de un formulario en el admin de Django que le solicita:

* **Formato** del archivo mediante el cual carga el nuevo catálogo (XLSX o JSON).
* **UPLOAD** del archivo con el nuevo catálogo

**Nota**: el formulario muestra qué catálogo se está modificando al cargar el archivo, pero no permite elegir otro.

Una vez subido, validado y guardado, el formulario muestra las URLs de descarga generadas desde donde se puede descargar el archivo en formato XLSX o JSON:

https://infra.datos.gob.ar/catalog/{catalog_id}/data.json
https://infra.datos.gob.ar/catalog/{catalog_id}/catalog.xlsx

### Validaciones

El catálogo que se carga debe superar perfectamente la validación de pydatajson `is_valid_catalog()` (0% de error). En caso de que esta no se pase exitosamente, se devuelve al usuario una lista de los errores encontrados en la interfaz web y se rechaza la carga / modificación del catálogo.

### Versionado de archivos

Los catálogos pisados reemplazan el contenido al que se puede acceder en https://infra.datos.gob.ar/catalog/{catalog_id}/data.json y https://infra.datos.gob.ar/catalog/{catalog_id}/catalog.xlsx, y a su vez generan una copia fechada en https://infra.datos.gob.ar/catalog/{catalog_id}/data-{iso_date}.json y https://infra.datos.gob.ar/catalog/{catalog_id}/catalog-{iso_date}.xlsx donde `iso_date` adopta la forma `YYYY-MM-DD` de la fecha en que se carga el archivo.

De esta manera, el sistema genera un versionado de los archivos cargados anteriormente que se mantiene accesible en caso de conocer la fecha de carga, pero la ruta con el nombre normal del catálogo se mantiene invariante.

### FTP

El mismo usuario y contraseña nominal que permiten acceder por interfaz web y cargar un archivo, permiten cargar un archivo en la ruta `/data-{iso_date}.json` y `/catalog-{iso_date}.xlsx` por FTP.

**En ningún caso, un usuario puede cargar o pisar un catálogo al cual no esté asociado y tenga permisos**.

### API

Los recursos de la API correspondientes a catálogos son:

#### Subir catálogo (`/api/upload-catalog`)
**Request:**
- URL: https://infra.datos.gob.ar/api/upload-catalog
- Método: **POST**
- Headers:
    - `Authorization`: Debe tomar el valor "Bearer " seguido del token.
- Parámetros (Querystring):
    - `format` **(requerido)**: Formato del catálogo (`xlsx` o `json`).
- Body: Contenido del archivo del catálogo sin procesar **(requerido)**.

Ejemplo:
```
curl -X POST https://infra.datos.gob.ar/api/upload-catalog?format=xlsx \
     --header "Authorization: Bearer <TOKEN>" \
     --header "Content-Type: application/octet-stream" \
     --data-binary @catalog.xlsx
```

**Response: 200 OK**
```json
{
	"urls": {
		"json": "https://infra.datos.gob.ar/catalog/1/data.json",
		"xlsx": "https://infra.datos.gob.ar/catalog/1/catalog.xlsx"
	},
	"replaced": false
}
```

**Response: 400 Bad Request**

Error de validación:
```json
{
	"error": {
		"code": 1000,
		"message": "El catálogo no es válido.",
		"failed_validations": [
			...
		]
	}
}
```

Error de formato/interpretación del archivo:
```json
{
	"error": {
		"code": 1001,
		"message": "No se pudo leer los contenidos del archivo."
	}
}
```

**Response: 403 Unauthorized**
```json
{
	"error": {
		"code": 1002,
		"message": "No se cuenta con los permisos necesarios para crear o modificar el catálogo."
	}
}
```
