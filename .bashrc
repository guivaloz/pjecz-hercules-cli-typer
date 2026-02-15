# pjecz-hercules-flask

if [ -f ~/.bashrc ]
then
    . ~/.bashrc
fi

if [[ "$TOOLBOX_NAME" != "pjecz-developer" ]]
then
    echo "-- Debe de ingresar al toolbox"
    echo "   toolbox enter pjecz-developer"
    echo
    exit 1
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
    # export $(grep -v '^#' .env | xargs)
    source .env && export $(sed '/^#/d' .env | cut -d= -f1)
    echo "   DB_HOST: ${DB_HOST}"
    echo "   DB_PORT: ${DB_PORT}"
    echo "   DB_NAME: ${DB_NAME}"
    echo "   DB_USER: ${DB_USER}"
    echo "   DB_PASS: ${DB_PASS}"
    echo "   GOOGLE_APPLICATION_CREDENTIALS: ${GOOGLE_APPLICATION_CREDENTIALS}"
    echo "   SQLALCHEMY_DATABASE_URI: ${SQLALCHEMY_DATABASE_URI}"
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
fi
