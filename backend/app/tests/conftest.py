import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["CHECKIN_EARLY_MINUTES"] = "100000"  # lets tests check in without waiting

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

API = "/api/v1"


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return TestClient(app)


def signup(c, email, role="user"):
    c.post(f"{API}/auth/register", json={"name": "Test User", "email": email, "password": "password123", "role": role})
    token = c.post(f"{API}/auth/login", json={"email": email, "password": "password123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
