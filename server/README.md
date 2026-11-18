# Server – FastAPI backend

FastAPI + SQLModel + PostgreSQL, structured by feature. Each team member works only inside their own feature folder.

```
server/
├── app/
│   ├── main.py            SHARED  FastAPI app, health checks, includes all 5 routers
│   ├── seed.py            SHARED  runs each feature's seed() once, when the database is empty
│   ├── core/              SHARED  config.py (env vars), database.py (engine, SessionDep, all tables),
│   │                              clock.py (UTC + Thailand time helpers)
│   └── features/
│       ├── f1_accounts/           F1  Wongsathorn Sereephap
│       ├── f2_record_collection/  F2  Masaaki Kato
│       ├── f3_crew_history/       F3  Kaung Khant Paing
│       ├── f4_verification/       F4  Hein Thant Si Thu
│       └── f5_fleet_boats/        F5  Natthachaimongkol Chayopathum
├── tests/                 same feature folders + shared conftest.py / test_health.py
├── Dockerfile, entrypoint.sh   image used by compose (dev) and Render (prod)
├── pyproject.toml, uv.lock     dependencies managed with uv
└── requirements.txt       exported from uv.lock - used by Docker and CI
```

Inside a feature folder: `router.py` (APIRouter), `schemas.py` (Pydantic In/Out models), `models.py` (SQLModel tables), `service.py` (logic), `seed.py` (demo data). Feature 1 also provides `dependencies.py` (`CurrentUser`, `require_role`) for everyone.

Database: tables, seed data, persistence and the rules for changing a model are in [`docs/DATABASE.md`](../docs/DATABASE.md).

## Run

Easiest – from the repository root: `docker compose up --build`, then open http://localhost:34242/docs.

Without Docker for the API (database still from compose: `docker compose up -d database`):

```bash
cd server
uv sync
uv run fastapi dev app/main.py --port 34242
```

## Test

```bash
docker compose exec backend python -m pytest -vv
# or, with the compose database running:
cd server && uv run pytest -vv
```

Tests use a separate database (`appdb_test`, created automatically), so they never touch your demo data.

## Add a dependency

Libraries not taught in ITCS525 need team approval first (docs/DECISIONS.md). Then:

```bash
cd server
uv add <package>
uv export --frozen --no-emit-project --format requirements-txt --output-file requirements.txt
```

Commit `pyproject.toml`, `uv.lock` and `requirements.txt` together, and rebuild the image (`docker compose up --build`).
