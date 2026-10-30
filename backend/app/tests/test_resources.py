from .conftest import API, signup

RES = {"name": "3D Printer", "category": "equipment", "location": "Lab 1", "requires_verification": False}


def test_only_staff_can_create_and_search_works(client):
    owner, user = signup(client, "o@demo.edu", "owner"), signup(client, "u@demo.edu")
    assert client.post(f"{API}/resources", json=RES, headers=user).status_code == 403
    assert client.post(f"{API}/resources", json=RES, headers=owner).status_code == 201
    found = client.get(f"{API}/resources?q=printer&category=equipment", headers=user).json()
    assert len(found) == 1
