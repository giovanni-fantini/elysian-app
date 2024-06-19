import uuid

import pytest
from sqlalchemy.orm import Session

from app.models import Person


@pytest.fixture
def seed_person(db_session: Session):
    person_id = str(uuid.uuid4())
    person = Person(id=person_id, name="Test User")
    db_session.add(person)
    db_session.commit()
    return person_id


def test_accept_webhook_add(client):
    payload = {
        "payload_type": "PersonAdded",
        "payload_content": {
            "person_id": str(uuid.uuid4()),
            "name": "Test User",
            "timestamp": "2023-10-10T12:34:56Z",
        },
    }
    response = client.post("/accept_webhook", json=payload)
    assert response.status_code == 200
    assert response.json() == {"detail": "Webhook processed successfully"}


def test_accept_webhook_rename(client, seed_person):
    payload_rename = {
        "payload_type": "PersonRenamed",
        "payload_content": {
            "person_id": seed_person,
            "name": "Updated User",
            "timestamp": "2023-10-11T12:34:56Z",
        },
    }
    response = client.post("/accept_webhook", json=payload_rename)
    assert response.status_code == 200
    assert response.json() == {"detail": "Webhook processed successfully"}


def test_accept_webhook_remove(client, seed_person):
    payload_remove = {
        "payload_type": "PersonRemoved",
        "payload_content": {
            "person_id": seed_person,
            "timestamp": "2023-10-12T12:34:56Z",
        },
    }
    response = client.post("/accept_webhook", json=payload_remove)
    assert response.status_code == 200
    assert response.json() == {"detail": "Webhook processed successfully"}


def test_get_name(client, seed_person):
    response = client.get(f"/get_name?person_id={seed_person}")
    assert response.status_code == 200
    assert response.json() == {"name": "Test User"}


def test_get_name_not_found(client):
    response = client.get("/get_name", params={"person_id": str(uuid.uuid4())})
    assert response.status_code == 404
    assert response.json() == {"detail": "Person not found"}


def test_invalid_payload_type(client):
    payload = {"payload_type": "InvalidType", "payload_content": {}}
    response = client.post("/accept_webhook", json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid input"}


def test_invalid_person_added_payload(client):
    payload = {
        "payload_type": "PersonAdded",
        "payload_content": {
            "person_id": "not-a-uuid",
            "name": "Test User",
            "timestamp": "2023-10-10T12:34:56Z",
        },
    }
    response = client.post("/accept_webhook", json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid input"}


def test_invalid_person_renamed_payload(client):
    payload = {
        "payload_type": "PersonRenamed",
        "payload_content": {
            "person_id": "not-a-uuid",
            "name": "Test User",
            "timestamp": "2023-10-10T12:34:56Z",
        },
    }
    response = client.post("/accept_webhook", json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid input"}


def test_invalid_person_removed_payload(client):
    payload = {
        "payload_type": "PersonRemoved",
        "payload_content": {
            "person_id": "not-a-uuid",
            "name": "Test User",
            "timestamp": "2023-10-10T12:34:56Z",
        },
    }
    response = client.post("/accept_webhook", json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid input"}


def test_person_renamed_not_found(client):
    payload = {
        "payload_type": "PersonRenamed",
        "payload_content": {
            "person_id": str(uuid.uuid4()),
            "name": "Test User",
            "timestamp": "2023-10-10T12:34:56Z",
        },
    }
    response = client.post("/accept_webhook", json=payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "Person not found"}


def test_person_removed_not_found(client):
    payload = {
        "payload_type": "PersonRemoved",
        "payload_content": {
            "person_id": str(uuid.uuid4()),
            "name": "Test User",
            "timestamp": "2023-10-10T12:34:56Z",
        },
    }
    response = client.post("/accept_webhook", json=payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "Person not found"}


def test_serve_nl_to_sql_html(client):
    response = client.get("/nl-to-sql")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text
