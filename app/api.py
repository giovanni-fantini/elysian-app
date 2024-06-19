from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import UUID4, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_db
from app.docs import (
    accept_webhook_examples,
    accept_webhook_responses,
    execute_custom_nl_query_examples,
    execute_custom_nl_query_responses,
    get_name_responses,
)
from app.models import (
    GetNameResponse,
    PersonAdded,
    PersonRemoved,
    PersonRenamed,
    QueryRequest,
    QueryResponse,
    WebhookPayload,
)
from app.services import (
    add_person,
    format_and_execute_sql,
    get_person,
    parse_openai_response,
    remove_person,
    rename_person,
    translate_nl_to_sql,
)

router = APIRouter()


@router.post(
    "/accept_webhook",
    responses=accept_webhook_responses,
    summary="Process Webhook Payload",
    description="Processes incoming webhook payloads and performs specific actions based on the payload type.",
)
def accept_webhook(
    payload: WebhookPayload = Body(..., examples=accept_webhook_examples),
    db: Session = Depends(get_db),
):
    """
    Process incoming webhook payloads and perform actions based on the payload type.

    Args:
        payload (WebhookPayload): The payload sent by the webhook.
        db (Session): The database session.

    Returns:
        dict: A success message if the webhook was processed successfully.

    Raises:
        HTTPException: When an error occurs (specified by status code and detail).
    """
    try:
        if payload.payload_type == "PersonAdded":
            person_data = PersonAdded(**payload.payload_content)
            add_person(db, person_data)
        elif payload.payload_type == "PersonRenamed":
            person_data = PersonRenamed(**payload.payload_content)
            if not rename_person(db, person_data):
                raise HTTPException(status_code=404, detail="Person not found")
        elif payload.payload_type == "PersonRemoved":
            person_data = PersonRemoved(**payload.payload_content)
            if not remove_person(db, person_data):
                raise HTTPException(status_code=404, detail="Person not found")
        else:
            raise HTTPException(status_code=400, detail="Invalid input")
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid input")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    return {"detail": "Webhook processed successfully"}


@router.get(
    "/get_name",
    response_model=GetNameResponse,
    responses=get_name_responses,
    summary="Fetch Person Name",
    description="Fetches the name of a person by their UUID.",
)
async def get_name(person_id: UUID4, db: Session = Depends(get_db)):
    """
    Fetch the name of a person by their UUID.

    Args:
        person_id (UUID4): The UUID of the person.
        db (Session): The database session.

    Returns:
        GetNameResponse: The name of the person if found.

    Raises:
        HTTPException: When an error occurs (specified by status code and detail).
    """
    try:
        person = get_person(db, person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return {"name": person.name}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Server error")


@router.post(
    "/execute_custom_nl_query",
    response_model=QueryResponse,
    responses=execute_custom_nl_query_responses,
    summary="Execute Custom Natural Language Query",
    description="Executes a custom natural language query and returns the result.",
)
async def execute_custom_nl_query(
    query_request: QueryRequest = Body(..., examples=execute_custom_nl_query_examples),
    db: Session = Depends(get_db),
):
    """
    Execute a custom natural language query.

    Args:
        query_request (QueryRequest): The natural language query.
        db (Session): The database session.

    Returns:
        QueryResponse: The result of the query execution.

    Raises:
        HTTPException: When an error occurs (specified by status code and detail).
    """
    try:
        # Convert natural language to SQL
        sql_info_raw = translate_nl_to_sql(query_request.natural_language_query)

        # Parse OpenAI response
        sql_info = parse_openai_response(sql_info_raw)

        # Format and Execute the SQL query
        result = format_and_execute_sql(db, sql_info)
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
