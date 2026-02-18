from __future__ import annotations

import re
from datetime import datetime
from uuid import uuid4

from app.models import DocumentType, EntryType, FinancialEntry, ScannedDocument
from app.repository import InMemoryRepository

_AMOUNT_REGEX = re.compile(r"(?:total|amount|net)\s*[:\-]?\s*\$?\s*(\d+(?:\.\d{1,2})?)", re.IGNORECASE)


def extract_total(text: str) -> float | None:
    match = _AMOUNT_REGEX.search(text)
    if not match:
        return None
    return float(match.group(1))


def infer_entry_type(document_type: DocumentType) -> EntryType:
    if document_type in (DocumentType.EMPLOYEE_PAYCHECK, DocumentType.RECEIPT):
        return EntryType.PAYABLE
    return EntryType.RECEIVABLE


def scan_document(
    repo: InMemoryRepository,
    *,
    user_id: str,
    store_id: str,
    file_name: str,
    raw_text: str,
    document_type: DocumentType,
) -> tuple[ScannedDocument, FinancialEntry | None]:
    repo.get_user(user_id)
    store = repo.get_store(store_id)
    if store.user_id != user_id:
        raise ValueError("Store does not belong to user")

    total = extract_total(raw_text)
    document = ScannedDocument(
        id=str(uuid4()),
        user_id=user_id,
        store_id=store_id,
        file_name=file_name,
        document_type=document_type,
        raw_text=raw_text,
        extracted_total=total,
    )
    repo.create_document(document)

    auto_entry = None
    if total:
        auto_entry = FinancialEntry(
            id=str(uuid4()),
            user_id=user_id,
            store_id=store_id,
            entry_type=infer_entry_type(document_type),
            amount=total,
            currency="USD",
            source_document_id=document.id,
            category=document_type.value,
            note=f"Auto-generated from {file_name}",
            captured_at=datetime.utcnow(),
        )
        repo.create_entry(auto_entry)

    return document, auto_entry
