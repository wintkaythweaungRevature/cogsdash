from app.models import DocumentType, EntryType
from app.repository import InMemoryRepository
from app.services import extract_total, infer_entry_type, scan_document


def test_extract_total_from_text() -> None:
    assert extract_total("Today sales total: $123.40") == 123.40


def test_infer_entry_type() -> None:
    assert infer_entry_type(DocumentType.EMPLOYEE_PAYCHECK) == EntryType.PAYABLE
    assert infer_entry_type(DocumentType.SALES_SLIP) == EntryType.RECEIVABLE


def test_scan_document_creates_auto_entry() -> None:
    repo = InMemoryRepository()
    user = repo.create_user("Owner", "owner@example.com")
    store = repo.create_store(user.id, "Store A", "Downtown")

    document, auto_entry = scan_document(
        repo,
        user_id=user.id,
        store_id=store.id,
        file_name="sales.txt",
        raw_text="net: 455.90",
        document_type=DocumentType.SALES_SLIP,
    )

    assert document.extracted_total == 455.90
    assert auto_entry is not None
    assert auto_entry.amount == 455.90
    assert auto_entry.entry_type == EntryType.RECEIVABLE


def test_summary_for_multiple_stores() -> None:
    repo = InMemoryRepository()
    user = repo.create_user("Owner", "owner@example.com")
    store_1 = repo.create_store(user.id, "Store A", None)
    store_2 = repo.create_store(user.id, "Store B", None)

    scan_document(
        repo,
        user_id=user.id,
        store_id=store_1.id,
        file_name="sales-1.txt",
        raw_text="total: 300",
        document_type=DocumentType.SALES_SLIP,
    )
    scan_document(
        repo,
        user_id=user.id,
        store_id=store_2.id,
        file_name="paycheck.txt",
        raw_text="amount: 100",
        document_type=DocumentType.EMPLOYEE_PAYCHECK,
    )

    summary = repo.summary(user.id)
    assert summary["receivable_total"] == 300.0
    assert summary["payable_total"] == 100.0
    assert summary["net_position"] == 200.0
