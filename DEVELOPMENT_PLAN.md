# BuchhaltungsButler MCP Server — Debug & Development Plan

## Phase 1: Critical Fixes (Week 1)

### 1.1 Fix Existing Tool Parameter Gaps
- [ ] `bb_get_receipt`: Add `get_file: bool = false` parameter
- [ ] `bb_list_receipts`: Add missing params (`order`, `include_offers`, `deleted`, `invoicenumber`, `due_date`)
- [ ] `bb_list_postings`: Add missing params (`date_last_action_from`, `date_last_action_to`, `postingaccount`, `cost_location`, `order`)
- [ ] `bb_create_invoice`: Add missing optional params (`contact_person_name`, `street`, `additional_addressline`, `zip`, `city`, `country`, `email`, `recurring_interval`, `recurring_date_next`, `date_of_supply`, `invoicenumber`, `correspondence`, `discount_type`, `discount_value`, `payment_conditions`, `due_days`, `final_provisions`, `show_bankdata`, `show_contactdata`, `item_description`, `customer_number`, `payment_reference`)

### 1.2 Fix Posting Creation
- [ ] `bb_create_posting` (free): Add `postingtext`, `postingaccount_debit`, `postingaccount_credit`, `vat`, `cost_location_two`
- [ ] `bb_create_posting` (receipt): Support multi-posting arrays (`postingtexts[]`, `vats[]`, `amounts[]`, `creditor`, `debtor`)
- [ ] `bb_create_posting` (transaction): Support multi-posting arrays + `oi_receipts_ids_by_customer`

### 1.3 Infrastructure
- [ ] Add proper error handling (API error codes → meaningful messages)
- [ ] Add retry logic with exponential backoff for 429/500/504
- [ ] Add logging (structured, configurable level)
- [ ] Add request timeout configuration
- [ ] Rate limit awareness (100 req/min per customer)

## Phase 2: High-Priority Missing Endpoints (Week 2)

### 2.1 Transaction Support
- [ ] `bb_list_transactions` — GET /transactions/get
- [ ] `bb_get_transaction` — GET /transactions/get/id_by_customer
- [ ] `bb_add_transaction` — POST /transactions/add
- [ ] `bb_add_batch_transactions` — POST /transactions/addBatch
- [ ] `bb_assign_receipt_to_transaction` — POST /transactions/assign/receipt
- [ ] `bb_unassign_receipt_from_transaction` — POST /transactions/unassign/receipt
- [ ] `bb_get_transaction_receipts` — POST /transactions/assigned-receipts/get

### 2.2 Receipt Management
- [ ] `bb_add_receipt` — POST /receipts/add (without file)
- [ ] `bb_delete_receipt` — POST /receipts/delete/id_by_customer
- [ ] `bb_restore_receipt` — POST /receipts/restore/id_by_customer
- [ ] `bb_add_batch_receipts` — POST /receipts/addBatch
- [ ] `bb_get_receipt_transactions` — POST /receipts/assigned-transactions/get

### 2.3 Posting Management
- [ ] `bb_unconfirm_free_posting` — POST /postings/unconfirm/free
- [ ] `bb_unconfirm_receipt_posting` — POST /postings/unconfirm/receipt
- [ ] `bb_assign_receipt_to_free_posting` — POST /postings/assign/receipt-to-free-posting

## Phase 3: Medium-Priority Features (Week 3)

### 3.1 Invoice Enhancements
- [ ] `bb_create_invoice_draft` — POST /invoices/create/draft
- [ ] `bb_create_e_invoice` — POST /invoices/create/e-invoice

### 3.2 Account Management
- [ ] `bb_add_account` — POST /accounts/add

### 3.3 Settings / Master Data
- [ ] `bb_add_creditor` — POST /settings/add/creditor
- [ ] `bb_add_debtor` — POST /settings/add/debtor
- [ ] `bb_update_creditor` — POST /settings/update/creditor
- [ ] `bb_update_debtor` — POST /settings/update/debtor
- [ ] `bb_add_postingaccount` — POST /settings/add/postingaccount
- [ ] `bb_update_postingaccount` — POST /settings/update/postingaccount

### 3.4 Batch Operations
- [ ] `bb_add_batch_free_postings` — POST /postings/add-batch/free
- [ ] `bb_add_batch_receipt_postings` — POST /postings/add-batch/receipts
- [ ] `bb_add_batch_transaction_postings` — POST /postings/add-batch/transactions
- [ ] `bb_batch_assign_receipts` — POST /transactions/assign-batch/receipt

## Phase 4: Low-Priority / Nice-to-Have (Week 4)

### 4.1 Cost Locations
- [ ] `bb_add_cost_location` — POST /cost-locations/add
- [ ] `bb_get_cost_locations` — POST /cost-locations/get
- [ ] `bb_update_cost_location` — POST /cost-locations/update
- [ ] `bb_delete_cost_location` — POST /cost-locations/delete

### 4.2 Batch Settings
- [ ] `bb_batch_create_creditors` — POST /settings/add-batch/creditors
- [ ] `bb_batch_create_debtors` — POST /settings/add-batch/debtors

## Phase 5: Testing & Documentation (Ongoing)

- [ ] Unit tests for all tools (mock API responses)
- [ ] Integration tests against sandbox
- [ ] API response type definitions (Pydantic models)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Version tagging and changelog
- [ ] Migration guide for breaking changes
