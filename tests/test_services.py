import pytest
import uuid
from datetime import datetime
from unittest.mock import patch
from sqlalchemy.orm import Session
from app.models import Person, PersonAdded, PersonRenamed, PersonRemoved
from app.services import add_person, rename_person, remove_person, get_person, translate_nl_to_sql, parse_openai_response, format_and_execute_sql

def test_add_person(db_session: Session):
    person_data = PersonAdded(
        person_id=uuid.UUID(str(uuid.uuid4())),
        name="Test User",
        timestamp=datetime.now()
    )
    new_person = add_person(db_session, person_data)
    assert new_person.id == str(person_data.person_id)
    assert new_person.name == person_data.name

def test_rename_person(db_session: Session):
    person_id = str(uuid.uuid4())
    person = Person(id=person_id, name="Original Name")
    db_session.add(person)
    db_session.commit()

    person_data = PersonRenamed(
        person_id=uuid.UUID(person_id),
        name="Updated Name",
        timestamp=datetime.now()
    )
    renamed_person = rename_person(db_session, person_data)
    assert renamed_person.name == "Updated Name"

def test_remove_person(db_session: Session):
    person_id = str(uuid.uuid4())
    person = Person(id=person_id, name="Test User")
    db_session.add(person)
    db_session.commit()

    person_data = PersonRemoved(
        person_id=uuid.UUID(person_id),
        timestamp=datetime.now()
    )
    remove_result = remove_person(db_session, person_data)
    assert remove_result is True
    removed_person = db_session.query(Person).filter(Person.id == person_id).first()
    assert removed_person is None

def test_get_person(db_session: Session):
    person_id = str(uuid.uuid4())
    person = Person(id=person_id, name="Test User")
    db_session.add(person)
    db_session.commit()

    retrieved_person = get_person(db_session, person_id)
    assert retrieved_person.id == person_id
    assert retrieved_person.name == "Test User"
    
def test_translate_nl_to_sql(mock_openai_client, mock_openai_response):
    nl_query = "What's the current name of person id: d59abfc4-3aae-4e29-875b-7b56e021ad42?"
    sql_info_raw = translate_nl_to_sql(nl_query)
    assert sql_info_raw.strip() == mock_openai_response.strip()

def test_parse_openai_response(mock_openai_response):
    sql_info = parse_openai_response(mock_openai_response)
    assert "query_template" in sql_info
    assert "params" in sql_info
    assert sql_info["params"]["person_id"] == "d59abfc4-3aae-4e29-875b-7b56e021ad42"

def test_format_and_execute_sql(db_session: Session):
    person_id = str(uuid.uuid4())
    person = Person(id=person_id, name="Test User")
    db_session.add(person)
    db_session.commit()
    
    sql_info = {
        "query_template": "SELECT * FROM people WHERE id=:id",
        "params": {"id": person_id}
    }
    result = format_and_execute_sql(db_session, sql_info)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == person_id
    assert result[0]["name"] == "Test User"