import uuid
from sqlalchemy import Column, String
from pydantic import BaseModel, UUID4
from typing import Optional, Dict, List, Any
from datetime import datetime
from app.db import Base

# SQLAlchemy Model
class Person(Base):
    __tablename__ = "people"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), index=True)

# Pydantic Models
class PersonBase(BaseModel):
    id: UUID4
    name: str

    class Config:
        from_attributes = True

class PersonAdded(BaseModel):
    person_id: UUID4
    name: str
    timestamp: datetime

class PersonRenamed(BaseModel):
    person_id: UUID4
    name: str
    timestamp: datetime

class PersonRemoved(BaseModel):
    person_id: UUID4
    timestamp: datetime

class WebhookPayload(BaseModel):
    payload_type: str
    payload_content: Dict
    
class GetNameResponse(BaseModel):
    name: Optional[str]

    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    natural_language_query: str

class QueryResponse(BaseModel):
    result: List[Dict[str, Any]]