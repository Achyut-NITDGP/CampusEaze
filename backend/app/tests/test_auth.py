from .conftest import API, signup


def test_register_login_me_and_duplicate(client):
    h = signup(client, "a@demo.edu")
    assert client.get(f"{API}/auth/me", headers=h).json()["email"] == "a@demo.edu"
    dup = client.post(f"{API}/auth/register", json={"name": "Again", "email": "a@demo.edu", "password": "password123"})
    assert dup.status_code == 409


def test_cannot_self_register_as_admin(client):
    r = client.post(f"{API}/auth/register", json={"name": "Evil", "email": "e@demo.edu", "password": "password123", "role": "admin"})
    assert r.status_code == 400
