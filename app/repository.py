from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.models import EntryType, FinancialEntry, ScannedDocument, Store, User


class InMemoryRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.stores: dict[str, Store] = {}
        self.documents: dict[str, ScannedDocument] = {}
        self.entries: dict[str, FinancialEntry] = {}

    def create_user(self, name: str, email: str) -> User:
        user = User(id=str(uuid4()), name=name, email=email)
        self.users[user.id] = user
        return user

    def create_store(self, user_id: str, name: str, location: Optional[str]) -> Store:
        if user_id not in self.users:
            raise ValueError("User not found")
        store = Store(id=str(uuid4()), user_id=user_id, name=name, location=location)
        self.stores[store.id] = store
        return store

    def create_document(self, document: ScannedDocument) -> ScannedDocument:
        self.documents[document.id] = document
        return document

    def create_entry(self, entry: FinancialEntry) -> FinancialEntry:
        self.entries[entry.id] = entry
        return entry

    def get_store(self, store_id: str) -> Store:
        store = self.stores.get(store_id)
        if not store:
            raise ValueError("Store not found")
        return store

    def get_user(self, user_id: str) -> User:
        user = self.users.get(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    def summary(self, user_id: str, store_id: Optional[str] = None) -> dict[str, float | datetime]:
        self.get_user(user_id)
        receivable = 0.0
        payable = 0.0
        last_updated = datetime.min

        for entry in self.entries.values():
            if entry.user_id != user_id:
                continue
            if store_id and entry.store_id != store_id:
                continue
            if entry.entry_type == EntryType.RECEIVABLE:
                receivable += entry.amount
            else:
                payable += entry.amount
            if entry.captured_at > last_updated:
                last_updated = entry.captured_at

        if last_updated == datetime.min:
            last_updated = datetime.utcnow()

        return {
            "receivable_total": round(receivable, 2),
            "payable_total": round(payable, 2),
            "net_position": round(receivable - payable, 2),
            "last_updated": last_updated,
        }


repo = InMemoryRepository()
