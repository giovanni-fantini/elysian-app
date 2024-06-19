from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_db
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
    responses={
        200: {"description": "Webhook processed successfully"},
        400: {"description": "Invalid input"},
        404: {"description": "Person not found"},
        500: {"description": "Server error"},
    },
)
def accept_webhook(payload: WebhookPayload, db: Session = Depends(get_db)):
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
    responses={
        200: {"description": "Name fetched successfully"},
        404: {"description": "Person not found"},
        422: {"description": "Invalid UUID format"},
        500: {"description": "Server error"},
    },
)
async def get_name(person_id: UUID4, db: Session = Depends(get_db)):
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
    responses={
        200: {"description": "Query executed successfully"},
        400: {"description": "Invalid input"},
        500: {"description": "Server error"},
    },
)
async def execute_custom_nl_query(
    query_request: QueryRequest, db: Session = Depends(get_db)
):
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
