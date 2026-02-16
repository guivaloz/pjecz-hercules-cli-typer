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
