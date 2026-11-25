import pytest
from app import create_app


@pytest.fixture
def client():
    return create_app("sqlite:///:memory:").test_client()


def make_member(client, email="nadia@iset.tn", paid=True):
    mid = client.post("/members", json={"name": "Nadia", "email": email}).get_json()["id"]
    if paid:
        client.post(f"/members/{mid}/dues")
    return mid


def make_event(client, capacity=2):
    return client.post("/events", json={
        "title": "Hackathon", "date": "2026-12-10T09:00", "capacity": capacity
    }).get_json()["id"]


def test_health(client):
    assert client.get("/health").status_code == 200


def test_health_returns_version(client, monkeypatch):
    monkeypatch.setenv("APP_VERSION", "1.0.0")
    assert client.get("/health").get_json()["version"] == "1.0.0"


def test_register_member(client):
    r = client.post(f"/events/{make_event(client)}/register",
                    json={"member_id": make_member(client)})
    assert r.status_code == 201


def test_unpaid_member_is_refused(client):
    mid = make_member(client, paid=False)
    r = client.post(f"/events/{make_event(client)}/register", json={"member_id": mid})
    assert r.status_code == 403


def test_duplicate_registration_is_refused(client):
    eid, mid = make_event(client), make_member(client)
    client.post(f"/events/{eid}/register", json={"member_id": mid})
    r = client.post(f"/events/{eid}/register", json={"member_id": mid})
    assert r.status_code == 409


def test_full_event_is_refused(client):
    eid = make_event(client, capacity=1)
    client.post(f"/events/{eid}/register", json={"member_id": make_member(client, "a@iset.tn")})
    r = client.post(f"/events/{eid}/register", json={"member_id": make_member(client, "b@iset.tn")})
    assert r.status_code == 409

def test_list_event_members(client):
    eid, mid = make_event(client), make_member(client)
    client.post(f"/events/{eid}/register", json={"member_id": mid})
    r = client.get(f"/events/{eid}/members")
    assert r.status_code == 200
    assert [m["name"] for m in r.get_json()] == ["Nadia"]
