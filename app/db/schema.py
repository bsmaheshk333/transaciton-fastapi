from sqlalchemy import (String, Column, JSON, DateTime)
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from typing import Optional, Dict


Base = declarative_base()


class WorkItemModelSqlSchema(Base):
    __tablename__ = "bot_api_workitemmodel"
    workitem_id = Column(String, primary_key=True)
    process_id = Column(String)
    comment = Column(String, nullable=True)
    state = Column(String)
    status = Column(String)
    detail = Column(JSON)
    exception_type = Column(String, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class WorkItemFilterRequestData(BaseModel):
    pid: str = Field(max_length=20)
    start_date: str = Field()
    end_date: str = Field()
    state: str = Field(max_length=20, default=None)
    status: str = Field(max_length=20, default=None)


class WorkItemResponse(BaseModel):
    workitem_id: str
    process_id: str
    comment: Optional[str]
    state: Optional[str]
    status: Optional[str]
    detail: Optional[Dict]
    exception_type: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
