import json
import re

from openai import OpenAI
from pydantic import UUID4
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Person, PersonAdded, PersonRemoved, PersonRenamed

client = OpenAI()


def add_person(db: Session, person_data: PersonAdded):
    new_person = Person(id=str(person_data.person_id), name=person_data.name)
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    return new_person


def rename_person(db: Session, person_data: PersonRenamed):
    person = db.query(Person).filter(Person.id == str(person_data.person_id)).first()
    if not person:
        return False

    person.name = person_data.name
    db.commit()
    db.refresh(person)
    return person


def remove_person(db: Session, person_data: PersonRemoved):
    person = db.query(Person).filter(Person.id == str(person_data.person_id)).first()
    if not person:
        return False

    db.delete(person)
    db.commit()
    return True


def get_person(db: Session, person_id: UUID4) -> Person:
    return db.query(Person).filter(Person.id == str(person_id)).first()


def translate_nl_to_sql(nl_query: str) -> dict:
    system_message = """
    Given the following SQL table in MariaDb, your job is to write safe queries given a user's request. \n
    Ensure that no dangerous operations can be performed on the database (like SQL injection or deletion of records). \n
        CREATE TABLE people (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255)
    )
    WITH SYSTEM VERSIONING
    """
    user_message = f"For the following question, write a valid MariaDB SQL query with placeholders for parameters and provide the parameters separately in JSON: {nl_query}"
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0, max_tokens=256
    )
    sql_info = response.choices[0].message.content
    # Parse SQL info from OpenAI response
    return sql_info.strip()


def parse_openai_response(response: str) -> dict:
    # Strip leading and trailing whitespace/newlines
    response = response.strip()

    # Extract SQL template
    sql_template_match = re.search(r"```sql\n(.*?)\n```", response, re.DOTALL)
    if not sql_template_match:
        raise ValueError("SQL template not found in response")
    sql_template = sql_template_match.group(1).strip()

    # Extract JSON params
    json_params_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
    if not json_params_match:
        raise ValueError("JSON parameters not found in response")
    params_json = json_params_match.group(1).strip()

    # Parse JSON parameters to a dictionary
    params = json.loads(params_json)

    return {"query_template": sql_template, "params": params}


def format_and_execute_sql(db: Session, sql_info: dict):
    query_template = sql_info.get("query_template")
    params = sql_info.get("params")

    try:
        # Print the template and parameters for debugging purposes
        print(f"Query template: {query_template}")
        print(f"Parameters: {params}")

        # Create a text query using SQLAlchemy's text construct
        query = text(query_template)

        # Validate SQL template
        if not query_template or not params:
            raise ValueError("Invalid SQL template or parameters")

        # Execute the SQL query
        result = db.execute(query, params)
        db.commit()

        # Fetch and format result rows
        rows = result.fetchall()

        columns = result.keys()
        results = [dict(zip(columns, row)) for row in rows]

        if not results:
            return "No results found."

        return results
    except SQLAlchemyError as e:
        db.rollback()
        raise e  # Raise SQLAlchemyError to be caught in endpoint
    except Exception as e:
        db.rollback()
        raise e  # Raise Exception to be caught in endpoint
