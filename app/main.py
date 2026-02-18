from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.models import DocumentType, FinancialEntry
from app.repository import repo
from app.schemas import (
    CreateFinancialEntryRequest,
    CreateFinancialEntryResponse,
    CreateStoreRequest,
    CreateUserRequest,
    DashboardSummary,
    ScanDocumentResponse,
)
from app.services import scan_document

app = FastAPI(title="CogsDash API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/users")
def create_user(request: CreateUserRequest) -> dict[str, str]:
    user = repo.create_user(request.name, request.email)
    return {"id": user.id, "name": user.name, "email": user.email}


@app.post("/stores")
def create_store(request: CreateStoreRequest) -> dict[str, str | None]:
    try:
        store = repo.create_store(request.user_id, request.name, request.location)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "id": store.id,
        "user_id": store.user_id,
        "name": store.name,
        "location": store.location,
    }


@app.post("/entries", response_model=CreateFinancialEntryResponse)
def create_financial_entry(request: CreateFinancialEntryRequest) -> CreateFinancialEntryResponse:
    try:
        repo.get_user(request.user_id)
        store = repo.get_store(request.store_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if store.user_id != request.user_id:
        raise HTTPException(status_code=400, detail="Store does not belong to user")

    entry = FinancialEntry(
        id=str(uuid4()),
        user_id=request.user_id,
        store_id=request.store_id,
        entry_type=request.entry_type,
        amount=request.amount,
        currency=request.currency,
        source_document_id=request.source_document_id,
        category=request.category,
        note=request.note,
        captured_at=datetime.utcnow(),
    )
    repo.create_entry(entry)
    return CreateFinancialEntryResponse(
        id=entry.id,
        entry_type=entry.entry_type,
        amount=entry.amount,
        currency=entry.currency,
    )


@app.post("/documents/scan", response_model=ScanDocumentResponse)
async def upload_and_scan(
    user_id: str = Form(...),
    store_id: str = Form(...),
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
) -> ScanDocumentResponse:
    raw_bytes = await file.read()
    raw_text = raw_bytes.decode("utf-8", errors="ignore")

    try:
        document, auto_entry = scan_document(
            repo,
            user_id=user_id,
            store_id=store_id,
            file_name=file.filename or "uploaded-file",
            raw_text=raw_text,
            document_type=document_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    response = ScanDocumentResponse(
        document_id=document.id,
        store_id=document.store_id,
        document_type=document.document_type,
        extracted_total=document.extracted_total,
        extracted_currency=document.extracted_currency,
        auto_entry=None,
    )

    if auto_entry:
        response.auto_entry = CreateFinancialEntryResponse(
            id=auto_entry.id,
            entry_type=auto_entry.entry_type,
            amount=auto_entry.amount,
            currency=auto_entry.currency,
        )

    return response


@app.get("/dashboard/{user_id}", response_model=DashboardSummary)
def dashboard(user_id: str, store_id: str | None = None) -> DashboardSummary:
    try:
        summary = repo.summary(user_id=user_id, store_id=store_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return DashboardSummary(
        user_id=user_id,
        store_id=store_id,
        receivable_total=summary["receivable_total"],
        payable_total=summary["payable_total"],
        net_position=summary["net_position"],
        last_updated=summary["last_updated"],
    )
