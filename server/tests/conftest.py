"""Shared pytest fixtures. SHARED FILE - add feature-specific fixtures in your
own test folder (e.g. tests/f1_accounts/conftest.py) to avoid merge conflicts.

Run all tests:  docker compose exec backend python -m pytest -vv
           or:  cd server && uv run pytest -vv   (needs: docker compose up -d database)

Tests use their OWN database: the name from DATABASE_URL plus "_test"
(appdb -> appdb_test). It is created automatically on the same PostgreSQL
server, so running the tests never deletes your demo data in appdb.
Before every test all tables are dropped, created again and seeded with the
same demo data as app/seed.py, so each test starts from the same state.
"""

import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

# ---- point the app at the test database BEFORE importing it ----
_main_url = make_url(
    os.getenv("DATABASE_URL", "postgresql://appuser:password@localhost:54242/appdb").replace(
        "postgresql://", "postgresql+psycopg2://", 1
    )
)
_test_db = f"{_main_url.database}_test"
with create_engine(_main_url, isolation_level="AUTOCOMMIT").connect() as conn:
    exists = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": _test_db}).first()
    if not exists:
        conn.execute(text(f'CREATE DATABASE "{_test_db}"'))
os.environ["DATABASE_URL"] = _main_url.set(database=_test_db).render_as_string(hide_password=False)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, SQLModel  # noqa: E402

from app.core.database import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import seed_all  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_database():
    """Every test starts from empty tables + the demo seed data."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_all(session)
    yield


@pytest.fixture
def db():
    """A database session for tests that check rows directly."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def client():
    """FastAPI TestClient (same tool as the Testing Backend API lecture)."""
    return TestClient(app)
