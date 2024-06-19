import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["OPENAI_API_KEY"] = "test-api-key"

from app.db import Base, engine_factory, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = engine_factory(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def mock_openai_response():
    return """
SQL Query with placeholders:
```sql
SELECT name FROM people WHERE id = :person_id;
```

Parameters in JSON:
```json
{
"person_id": "d59abfc4-3aae-4e29-875b-7b56e021ad42"
}
```
"""


@pytest.fixture(scope="module")
def mock_openai_error_response():
    return """Some invalid response or error message"""


# Mock the OpenAI client for tests
@pytest.fixture(scope="module")
def mock_openai_client(mock_openai_response):
    with patch("app.services.client") as mock_client:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock(content=mock_openai_response)
        mock_client.chat.completions.create.return_value = mock_response
        yield mock_client


# Mock the OpenAI client for tests
@pytest.fixture(scope="module")
def mock_openai_error_client(mock_openai_error_response):
    with patch("app.services.client") as mock_client:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock(content=mock_openai_error_response)
        mock_client.chat.completions.create.return_value = mock_response
        yield mock_client


# Create a fixture for the FastAPI test client
@pytest.fixture(scope="module")
def client(setup_database, mock_openai_client):
    return TestClient(app)


# Create a fixture for setting up the database
@pytest.fixture(scope="module")
def setup_database():
    # Setup: Create the tables
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: Drop the tables
    Base.metadata.drop_all(bind=engine)


# Create a fixture for the database session
@pytest.fixture
def db_session(setup_database):
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
