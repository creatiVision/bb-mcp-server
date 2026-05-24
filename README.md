# BuchhaltungsButler MCP Server

MCP server wrapping the BuchhaltungsButler REST API for invoice/accounting automation.

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   # stdio mode (for MCP clients)
   python server.py --transport stdio

   # HTTP/SSE mode (port 8000)
   python server.py
   ```

## API Reference

- Docs: https://app.buchhaltungsbutler.de/docs/api/v1/
- Swagger: https://app.buchhaltungsbutler.de/docs/api/v1.de.json
- API version: 1.9.1

## Authentication

Uses HTTP Basic Auth (API Client + API Secret) plus `api_key` in the JSON body for customer selection.

## Implemented Tools (14/48 API endpoints)

### Receipts (Belege)
- `bb_list_receipts` — List receipts (inbound/outbound)
- `bb_get_receipt` — Get single receipt by id_by_customer
- `bb_upload_receipt` — Upload receipt file (PDF/image)

### Invoices (Rechnungen)
- `bb_create_invoice` — Create an invoice

### Accounts (Konten)
- `bb_list_accounts` — List all accounts

### Postings (Buchungssätze)
- `bb_list_postings` — List postings
- `bb_create_posting` — Create posting (free/receipt/transaction)

### Settings
- `bb_list_debtors` — List debtors (Debitoren)
- `bb_list_creditors` — List creditors (Kreditoren)
- `bb_list_postingaccounts` — List posting accounts

### Comments
- `bb_add_comment` — Add comment to receipt or transaction

## Missing API Endpoints (34)

### High Priority
- `receipts/add` — Add receipt without file
- `receipts/delete/id_by_customer` — Delete receipt
- `receipts/restore/id_by_customer` — Restore deleted receipt
- `receipts/addBatch` — Batch add receipts
- `receipts/assigned-transactions/get` — Get transactions for receipt
- `transactions/get` — List transactions
- `transactions/get/id_by_customer` — Get single transaction
- `transactions/assign/receipt` — Assign receipt to transaction
- `transactions/unassign/receipt` — Unassign receipt from transaction
- `transactions/assigned-receipts/get` — Get receipts for transaction
- `postings/unconfirm/free` — Unconfirm free posting
- `postings/unconfirm/receipt` — Unconfirm receipt posting
- `postings/assign/receipt-to-free-posting` — Assign receipt to free posting

### Medium Priority
- `invoices/create/draft` — Create invoice draft
- `invoices/create/e-invoice` — Create e-invoice
- `accounts/add` — Add a basic account
- `settings/add/creditor` — Create creditor
- `settings/add/debtor` — Create debtor
- `settings/update/creditor` — Update creditor
- `settings/update/debtor` — Update debtor
- `settings/add/postingaccount` — Add posting account
- `settings/update/postingaccount` — Update posting account
- `postings/add-batch/free` — Batch add free postings
- `postings/add-batch/receipts` — Batch add receipt postings
- `postings/add-batch/transactions` — Batch add transaction postings
- `transactions/add` — Add transaction
- `transactions/addBatch` — Batch add transactions
- `transactions/assign-batch/receipt` — Batch assign receipts

### Low Priority
- `cost-locations/add` — Add cost location
- `cost-locations/get` — Get cost locations
- `cost-locations/update` — Update cost location
- `cost-locations/delete` — Delete cost location
- `settings/add-batch/creditors` — Batch create creditors
- `settings/add-batch/debtors` — Batch create debtors

## Known Issues

- `bb_get_receipt`: Missing `get_file` parameter (to download file as base64)
- `bb_list_receipts`: Missing `order`, `include_offers`, `deleted`, `invoicenumber`, `due_date` params
- `bb_list_postings`: Missing `date_last_action_from`, `date_last_action_to`, `postingaccount`, `cost_location`, `order` params
- `bb_create_posting` (free): Missing `postingtext`, `postingaccount_debit`, `postingaccount_credit`, `vat`, `cost_location_two` params
- `bb_create_posting` (receipt/transaction): Missing multi-posting support (`postingtexts`, `vats`, `amounts`, `creditor`, `debtor`)
- No error handling for API rate limits (100 req/min)
- No retry logic for transient failures
- No logging
- No tests
