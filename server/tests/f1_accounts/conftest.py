"""Feature 1 fixtures (own folder, so the shared conftest.py stays untouched).

The shared conftest.py already gives every test a fresh test database with
the demo users (app/features/f1_accounts/seed.py).
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def f1_client():
    # https base URL: the session cookie is Secure when COOKIE_SECURE=true
    return TestClient(app, base_url="https://testserver")
