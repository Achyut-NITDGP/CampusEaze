from datetime import datetime, timedelta

from .conftest import API, signup

RES = {"name": "Oscilloscope", "category": "equipment", "location": "Lab 2", "requires_verification": False}


def test_full_lifecycle_with_waitlist(client):
    owner, u1, u2 = signup(client, "o@demo.edu", "owner"), signup(client, "u1@demo.edu"), signup(client, "u2@demo.edu")
    rid = client.post(f"{API}/resources", json=RES, headers=owner).json()["id"]
    d = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    body = {"resource_id": rid, "start_time": d.isoformat(), "end_time": (d + timedelta(hours=1)).isoformat(), "purpose": "Signal testing"}

    b = client.post(f"{API}/bookings", json=body, headers=u1).json()
    assert b["status"] == "pending"
    assert client.post(f"{API}/bookings/{b['id']}/decision", json={"decision": "approve"}, headers=u1).status_code == 403
    assert client.post(f"{API}/bookings/{b['id']}/decision", json={"decision": "approve"}, headers=owner).json()["status"] == "approved"

    # same slot -> waiting list, never a double booking
    assert client.post(f"{API}/bookings", json=body, headers=u2).json()["status"] == "waitlisted"

    ok = {"checklist_ok": True, "condition_notes": "Clean"}
    assert client.post(f"{API}/handover/{b['id']}/check-in", json=ok, headers=u1).status_code == 200
    assert client.post(f"{API}/handover/{b['id']}/check-out", json=ok, headers=u1).status_code == 200
    detail = client.get(f"{API}/bookings/{b['id']}", headers=u1).json()
    assert detail["status"] == "completed" and len(detail["reports"]) == 2 and len(detail["timeline"]) >= 4


def test_damage_goes_to_human_review(client):
    owner, u1 = signup(client, "o@demo.edu", "owner"), signup(client, "u1@demo.edu")
    rid = client.post(f"{API}/resources", json=RES, headers=owner).json()["id"]
    d = (datetime.now() + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    b = client.post(f"{API}/bookings", json={"resource_id": rid, "start_time": d.isoformat(), "end_time": (d + timedelta(hours=1)).isoformat(), "purpose": "Testing"}, headers=u1).json()
    client.post(f"{API}/bookings/{b['id']}/decision", json={"decision": "approve"}, headers=owner)
    client.post(f"{API}/handover/{b['id']}/check-in", json={"checklist_ok": True}, headers=u1)
    client.post(f"{API}/handover/{b['id']}/check-out", json={"checklist_ok": False, "damage_reported": True, "condition_notes": "Probe cracked"}, headers=u1)
    assert client.get(f"{API}/bookings/{b['id']}", headers=u1).json()["status"] == "disputed"
    inc = client.get(f"{API}/incidents?scope=managed", headers=owner).json()
    assert inc and inc[0]["status"] == "open"
