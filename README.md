# pjecz-hercules-cli-typer

Interfaz de linea de comandos hecha con Typer y Python para Plataforma Web.

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

Crear un bash script para entrar al entorno virtual y cargar las variables de entorno

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

if [ -f .env ]
then
    echo "-- Variables de entorno"
    export $(grep -v '^#' .env | xargs)
    echo "   DB_HOST: ${DB_HOST}"
    echo "   DB_PORT: ${DB_PORT}"
    echo "   DB_NAME: ${DB_NAME}"
    echo "   DB_USER: ${DB_USER}"
    echo "   DB_PASS: ${DB_PASS}"
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
    alias cli="uv run ${PWD}/pjecz_hercules_cli_typer/app.py"
    echo "-- Ejecutar el CLI"
    echo "   cli --help"
    echo
fi
```

## Uso

Consultar las materias

```bash
cli materias query
```

Consultar un distrito por su clave

```bash
cli distritos query --clave dslt
```

Consultar una autoridad por su clave

```bash
cli autoridades query --clave slt-j1-fam
```

Consultar las autoridades que sean Tribunales Laborales

```bash
cli autoridades query --clave tl
```

Consultar las autoridades que sean Notarías de Torreón, con offset 40 y limit 40

```bash
cli autoridades query --clave trc-n --offset 40 --limit 40
```

Consultar los 40 edictos más recientes

```bash
cli edictos query --limit 40
```

Consultar los 40 edictos más recientes de la Notaría 66

```bash
cli edictos query --autoridad-clave slt-n066 --limit 40
```

Mostrar 20 edictos que se pueden actualizar de la autoridad TRC-N027, con offset 40, sin guardar los cambios

```bash
cli edictos update --autoridad-clave trc-n027 --limit 20 --offset 40
```

Actualizar 20 edictos de la autoridad TRC-N027, con offset 40 y guardar los cambios

```bash
cli edictos update --autoridad-clave trc-n027 --limit 20 --offset 40 --save
```
