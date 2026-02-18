from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models import DocumentType, EntryType


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class CreateStoreRequest(BaseModel):
    user_id: str
    name: str = Field(min_length=2, max_length=120)
    location: Optional[str] = None


class CreateFinancialEntryRequest(BaseModel):
    user_id: str
    store_id: str
    entry_type: EntryType
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    category: str = Field(min_length=2, max_length=80)
    note: Optional[str] = None
    source_document_id: str = Field(min_length=8)


class CreateFinancialEntryResponse(BaseModel):
    id: str
    entry_type: EntryType
    amount: float
    currency: str


class ScanDocumentResponse(BaseModel):
    document_id: str
    store_id: str
    document_type: DocumentType
    extracted_total: Optional[float]
    extracted_currency: str
    auto_entry: Optional[CreateFinancialEntryResponse] = None


class DashboardSummary(BaseModel):
    user_id: str
    store_id: Optional[str] = None
    receivable_total: float
    payable_total: float
    net_position: float
    last_updated: datetime
