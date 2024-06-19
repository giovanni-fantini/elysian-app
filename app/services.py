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
    """
    Add a new person to the database.

    Args:
        db (Session): The database session.
        person_data (PersonAdded): The data of the person to add.

    Returns:
        Person: The newly added person.
    """
    new_person = Person(id=str(person_data.person_id), name=person_data.name)
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    return new_person


def rename_person(db: Session, person_data: PersonRenamed):
    """
    Rename an existing person in the database.

    Args:
        db (Session): The database session.
        person_data (PersonRenamed): The data of the person to rename.

    Returns:
        Person: The renamed person, or False if the person was not found.
    """
    person = db.query(Person).filter(Person.id == str(person_data.person_id)).first()
    if not person:
        return False

    person.name = person_data.name
    db.commit()
    db.refresh(person)
    return person


def remove_person(db: Session, person_data: PersonRemoved):
    """
    Remove an existing person from the database.

    Args:
        db (Session): The database session.
        person_data (PersonRemoved): The data of the person to remove.

    Returns:
        bool: True if the person was removed successfully, otherwise False.
    """
    person = db.query(Person).filter(Person.id == str(person_data.person_id)).first()
    if not person:
        return False

    db.delete(person)
    db.commit()
    return True


def get_person(db: Session, person_id: UUID4) -> Person:
    """
    Get a person by their UUID.

    Args:
        db (Session): The database session.
        person_id (UUID4): The UUID of the person to retrieve.

    Returns:
        Person: The person if found, otherwise None.
    """
    return db.query(Person).filter(Person.id == str(person_id)).first()


def translate_nl_to_sql(nl_query: str) -> dict:
    """
    Translate a natural language query to SQL using OpenAI.

    Args:
        nl_query (str): The natural language query.

    Returns:
        dict: The SQL information obtained from the query.
    """
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
    return sql_info.strip()


def parse_openai_response(response: str) -> dict:
    """
    Parse the response from OpenAI to extract SQL template and parameters.

    Args:
        response (str): The OpenAI response.

    Returns:
        dict: The SQL template and optionally the parameters extracted from the response.

    Raises:
        ValueError: If the SQL template or JSON parameters are not found.
    """
    response = response.strip()

    # Extract SQL template
    sql_template_match = re.search(r"```sql\n(.*?)\n```", response, re.DOTALL)
    if not sql_template_match:
        raise ValueError("SQL template not found in response")
    sql_template = sql_template_match.group(1).strip()

    # Extract JSON params
    json_params_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
    if json_params_match:
        params_json = json_params_match.group(1).strip()
        params = json.loads(params_json)
    else:
        params = None  # No parameters found

    return {"query_template": sql_template, "params": params}


def format_and_execute_sql(db: Session, sql_info: dict):
    """
    Format and execute the provided SQL query.

    Args:
        db (Session): The database session.
        sql_info (dict): The SQL template and optionally parameters.

    Returns:
        dict: The formatted results to be returned.

    Raises:
        SQLAlchemyError: If an SQL execution error occurs.
        Exception: For any other exceptions.
    """
    query_template = sql_info.get("query_template")
    params = sql_info.get("params")

    try:
        # Print the template and parameters for debugging purposes
        print(f"Query template: {query_template}")
        print(f"Parameters: {params}")

        # Create a text query using SQLAlchemy's text construct
        query = text(query_template)

        # Possibility of params being None
        if params:
            result = db.execute(query, params)
        else:
            result = db.execute(query)

        db.commit()

        # Fetch and format result rows
        rows = result.fetchall()
        columns = result.keys()
        results = [dict(zip(columns, row)) for row in rows]
        print(results)
        if not results:
            return "No results found."

        return results
    except SQLAlchemyError as e:
        db.rollback()
        raise e  # Raise SQLAlchemyError to be caught in endpoint
    except Exception as e:
        db.rollback()
        raise e  # Raise Exception to be caught in endpoint
