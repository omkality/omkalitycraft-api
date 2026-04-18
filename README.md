# OmkalityCraft API

[![Python](https://img.shields.io/badge/python-3.14.2-blue.svg)](https://www.python.org/)
[![Litestar](https://img.shields.io/badge/Litestar-2.x-202235.svg)](https://litestar.dev/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Types](https://img.shields.io/badge/types-mypy-2A6DB2.svg)](https://mypy-lang.org/)

CDN + API для лаунчера OmkalityCraft.

## Требования

- Python 3.14.2
- uv
- Docker и Docker Compose, если запускаете в контейнере

## Переменные окружения

`.env`:

```env
API_HOST=0.0.0.0
API_PORT=8000
WORKERS_NUM=4
HOST_CONTENT_ROOT=./data/content
CONTENT_ROOT=/data/content
```

Структура контента:

```text
data/content/
  launcher/
    files/
    manifest.json
  instances/
    <instance_id>/
      files/
      manifest.json
      instance_config.json
      launch_profile.json
```

## Запуск через Docker Compose

```powershell
docker compose up -d --build
```

Проверка:

```powershell
curl http://localhost:8000/health
```

```powershell
curl http://localhost:8000/version
```

Остановка:

```powershell
docker compose down
```

## Виртуальное окружение для разработки

Создать виртуальное окружение и установить зависимости из всех групп:

```powershell
uv venv --python 3.14.2
```

```powershell
uv sync --all-groups
```

Активировать окружение в PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## Проверка качества кода

Установить pre-commit hooks:

```powershell
uv run pre-commit install
```

Запустить все проверки вручную:

```powershell
uv run pre-commit run --all-files
```

## Подготовка CDN-контента

Собрать `data/content` из локального лаунчера:

```powershell
uv run python scripts/stage_launcher_content.py --source-root C:\Users\omka\Projects\omkality_launcher
```

Скрипт копирует bootstrap-файлы лаунчера, `divinejourney2`, создаёт
`instance_config.json`, `launch_profile.json` и генерирует manifest-файлы.
Правила берутся из `src/settings`.

После запуска API можно проверить endpoints:

```powershell
curl http://localhost:8000/instances
```

```powershell
curl http://localhost:8000/launcher/manifest
```

```powershell
curl http://localhost:8000/instances/divinejourney2/launch-profile
```

Текущий CLI-прототип лаунчера лежит в `client/launcher.py`. Для ручной проверки
его можно положить в корень тестовой копии лаунчера и запустить:

```powershell
$env:OMKALITY_API_URL="http://localhost:8000"
```

```powershell
python launcher.py
```

## Генерация манифестов

Манифест лаунчера:

```powershell
uv run python scripts/generate_manifest.py launcher
```

Манифест инстанса:

```powershell
uv run python scripts/generate_manifest.py instance divinejourney2
```

Настройки manifest, `instance_config` и `launch_profile` лежат здесь:

```text
src/settings/launcher/manifest.json
src/settings/instances/divinejourney2/manifest.json
src/settings/instances/divinejourney2/instance_config.json
src/settings/instances/divinejourney2/launch_profile.json
```

Например, JVM-память меняется в `launch_profile.json`, а правила игнора и
soft-managed файлов — в `instance_config.json`.

## Документация API

После запуска Swagger UI доступен по адресу:

```text
http://localhost:8000/docs
```

Корневой адрес `http://localhost:8000` автоматически перенаправляет на документацию.
