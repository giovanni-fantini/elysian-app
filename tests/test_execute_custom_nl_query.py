import pytest
from app.models import QueryRequest
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch

def test_execute_custom_nl_query(client, mock_openai_client, db_session):
    query_request = QueryRequest(natural_language_query="What's the current name of person id: d59abfc4-3aae-4e29-875b-7b56e021ad42?")
    # Insert test data as the setup
    db_session.execute("INSERT INTO people (id, name) VALUES ('d59abfc4-3aae-4e29-875b-7b56e021ad42', 'Test User')")
    db_session.commit()
    response = client.post("/execute_custom_nl_query", json=query_request.model_dump())
    assert response.status_code == 200
    response_json = response.json()
    assert "result" in response_json
    result = response_json["result"]
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["name"] == "Test User"

def test_sql_execution_error(client, mock_openai_client):
    query_request = QueryRequest(natural_language_query="What's the previous name of person id: d59abfc4-3aae-4e29-875b-7b56e021ad42?")
    
    # Mocking a SQLAlchemy execution failure
    with patch("sqlalchemy.orm.session.Session.execute", side_effect=SQLAlchemyError('SQL execution error')):
        response = client.post("/execute_custom_nl_query", json=query_request.model_dump())
        assert response.status_code == 400
        assert "detail" in response.json()
        assert response.json()["detail"] == "SQL execution error: SQL execution error"

def test_invalid_sql_query(client, mock_openai_error_client):
    query_request = QueryRequest(natural_language_query="This is an invalid query")
    response = client.post("/execute_custom_nl_query", json=query_request.model_dump())
    assert response.status_code == 400
    assert "detail" in response.json()
        