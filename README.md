# pjecz-hercules-cli-typer

Interfaz de linea de comandos hecha con Typer y Python para Plataforma Web.

## Objetivo

Comandos para el mantenimiento de la base de datos Plataforma Web.

Cada comando trabaja en la tabla del mismo nombre.

El subcomando es un verbo que determina la accion a realizar, por ejemplo, consultar, exportar, etc.

## Instalación

Crear entorno virtual

```bash
python -m venv .venv
```

Activar entorno virtual

```bashbash
source .venv/bin/activate  # Linux/Mac
```

Instalar dependencias

```bash
uv sync
```

Crear un archivo para las variables de entorno

```bash
cp .env.example .env
```

Crear un archivo `.bashrc` que facilite la carga de las variables de entorno y del entorno Python

```bash
# pjecz-hercules-cli-typer

if [ -f ~/.bashrc ]
then
    . ~/.bashrc
fi

if command -v figlet &> /dev/null
then
    figlet Hercules CLI Typer
else
    echo "== Hercules CLI Typer"
fi
echo

# Google Application Credentials
export GOOGLE_APPLICATION_CREDENTIALS=

if [ -f .env ]
then
    export $(grep -v '^#' .env | xargs)
    echo "-- Variables de entorno"
    echo "   CLOUD_STORAGE_DEPOSITO_EDICTOS: ${CLOUD_STORAGE_DEPOSITO_EDICTOS}"
    echo "   CLOUD_STORAGE_DEPOSITO_GLOSAS: ${CLOUD_STORAGE_DEPOSITO_GLOSAS}"
    echo "   CLOUD_STORAGE_DEPOSITO_LISTAS_DE_ACUERDOS: ${CLOUD_STORAGE_DEPOSITO_LISTAS_DE_ACUERDOS}"
    echo "   CLOUD_STORAGE_DEPOSITO_OFICIOS: ${CLOUD_STORAGE_DEPOSITO_OFICIOS}"
    echo "   CLOUD_STORAGE_DEPOSITO_SENTENCIAS: ${CLOUD_STORAGE_DEPOSITO_SENTENCIAS}"
    echo "   DB_HOST: ${DB_HOST}"
    echo "   DB_PORT: ${DB_PORT}"
    echo "   DB_NAME: ${DB_NAME}"
    echo "   DB_USER: ${DB_USER}"
    echo "   DB_PASS: ${DB_PASS}"
    echo "   SALT: ${SALT}"
    echo "   SQLALCHEMY_DATABASE_URI: ${SQLALCHEMY_DATABASE_URI}"
    echo "   TZ: ${TZ}"
    echo
    export PGHOST=$DB_HOST
    export PGPORT=$DB_PORT
    export PGDATABASE=$DB_NAME
    export PGUSER=$DB_USER
    export PGPASSWORD=$DB_PASS
fi

if [ -d .venv ]
then
    echo "-- Python Virtual Environment"
    source .venv/bin/activate
    echo "   $(python3 --version)"
    export PYTHONPATH=$(pwd)
    echo "   PYTHONPATH: ${PYTHONPATH}"
    echo
    alias cli="uv run ${PWD}/src/pjecz_hercules_cli_typer/main.py"
    echo "-- Ejecutar el CLI"
    echo "   cli --help"
    echo
fi
```
