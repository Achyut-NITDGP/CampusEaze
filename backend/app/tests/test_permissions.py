from .conftest import API, signup


def test_requires_auth_and_roles(client):
    assert client.get(f"{API}/bookings").status_code == 401
    user = signup(client, "u@demo.edu")
    assert client.get(f"{API}/admin/audit-logs", headers=user).status_code == 403
    assert client.get(f"{API}/users", headers=user).status_code == 403
