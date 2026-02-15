# pjecz-hercules-cli-typer

Interfaz de linea de comandos hecha con Typer y Python para Plataforma Web.

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

Consultar los 40 edictos más recientes

```bash
cli edictos query --limit 40
```

Consultar los 40 edictos más recientes de la Notaría 66

```bash
cli edictos query --autoridad-clave slt-n066 --limit 40
```
