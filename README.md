# CogsDash (MVP)

A starter backend for a restaurant finance dashboard that can:

- Support one user managing multiple stores.
- Scan uploaded slip/paycheck/sales text files (placeholder for OCR).
- Classify records into **receivables** and **payables**.
- Produce a dashboard summary similar to a lightweight Power BI home view.

> Note: OCR is mocked by reading uploaded file text. In production, replace this with an OCR provider (Google Vision, AWS Textract, Azure Document Intelligence, or Tesseract).

## API features

- `POST /users` create account owner.
- `POST /stores` create multiple stores under a user.
- `POST /documents/scan` upload a slip/paycheck/sales doc and auto-generate a financial entry when amount is detected.
- `POST /entries` add manual receivable/payable entries.
- `GET /dashboard/{user_id}` aggregate receivables/payables and net position, optionally filtered by `store_id`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open: `http://127.0.0.1:8000/docs`

## Example flow

1. Create user.
2. Create multiple stores for that user.
3. Upload a sales slip/paycheck text file to `/documents/scan`.
4. View dashboard summary from `/dashboard/{user_id}`.

## Data model (MVP)

- **User**: business owner/admin.
- **Store**: belongs to a user.
- **ScannedDocument**: the extracted data from uploaded photo/slip text.
- **FinancialEntry**: receivable/payable ledger row tied to source document.

## Next steps to production

1. Replace file-text scanning with OCR pipeline (image preprocessing + OCR + structured extraction).
2. Add authentication (JWT + RBAC).
3. Move in-memory repository to Postgres.
4. Add front-end dashboard (React + charting) with per-store KPI cards.
5. Add job queue for async processing and retry.
