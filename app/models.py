from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class DocumentType(str, Enum):
    SALES_SLIP = "sales_slip"
    EMPLOYEE_PAYCHECK = "employee_paycheck"
    INVOICE = "invoice"
    RECEIPT = "receipt"


class EntryType(str, Enum):
    RECEIVABLE = "receivable"
    PAYABLE = "payable"


@dataclass
class User:
    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Store:
    id: str
    user_id: str
    name: str
    location: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FinancialEntry:
    id: str
    user_id: str
    store_id: str
    entry_type: EntryType
    amount: float
    currency: str
    source_document_id: str
    category: str
    note: Optional[str] = None
    captured_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScannedDocument:
    id: str
    user_id: str
    store_id: str
    file_name: str
    document_type: DocumentType
    raw_text: str
    extracted_total: Optional[float]
    extracted_currency: str = "USD"
    created_at: datetime = field(default_factory=datetime.utcnow)
