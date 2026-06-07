# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CLI para la Plataforma Web del Poder Judicial del Estado de Coahuila de Zaragoza. Manages judicial data (edictos, digitalizaciones, autoridades, etc.) stored in PostgreSQL, with file management in Google Cloud Storage.

## Setup

```bash
# Install dependencies (uses uv)
uv sync

# Configure environment
cp .env.example .env  # edit with PostgreSQL credentials and GCS settings
```

The `.env` file must define PostgreSQL connection (`SQLALCHEMY_DATABASE_URI`) and GCS credentials (`CLOUD_STORAGE_DEPOSITO`).

## Development Commands

```bash
# Run a command
python -m pjecz_hercules_cli_typer.app <resource> <action> [options]

# Or if installed as CLI tool
cli <resource> <action> [options]

# Linting / formatting
black .
isort .
ruff check .
basedpyright
```

## Architecture

**Entry point**: `pjecz_hercules_cli_typer/app.py` — registers all Typer subcommands.

**Directory layout**:
- `commands/` — one file per resource (autoridades, edictos, vsp_digitalizaciones, etc.). Each file creates its own `typer.Typer()` app and registers actions (`query`, `update`, `actualizar`).
- `models/` — SQLAlchemy ORM models. Models map 1:1 to database tables and define relationships.
- `config/settings.py` — Pydantic `BaseSettings` reads `.env` and exposes a singleton `get_settings()`.
- `utils/database.py` — SQLAlchemy engine + session factory, exposes `Base` and `get_db()` session context.
- `utils/google_cloud_storage.py` — GCS helpers: blob existence check, copy+delete rename, upload, download.
- `utils/safe_string.py` — input validation/normalization for claves, emails, expediente numbers.

**Command pattern**: `cli <resource> <action> [--clave X] [--limit N] [--offset N] [--save]`
- Without `--save`, commands are dry-run (query only, no writes).
- `--save` commits database changes and/or performs GCS operations.

**GCS file rename flow** (used in `edictos update` and `vsp_digitalizaciones actualizar`):
1. Build expected blob name from record fields.
2. Check if blob exists in the bucket.
3. If name differs from stored value: copy to new name, delete old blob, update DB record.

**Rich output**: All commands use `rich.console.Console` for colored output and `rich.table.Table` for tabular results.

## Code Conventions

- Code, comments, and variable names are in Spanish.
- Black line length: 128 characters.
- Imports sorted with isort (black-compatible profile).
- Type hints are used throughout; Pydantic and SQLModel handle validation.
