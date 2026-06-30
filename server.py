#!/usr/bin/env python3
"""
BuchhaltungsButler MCP Server v2.0
Complete coverage of all 48 API endpoints (v1.9.1).

API Docs: https://app.buchhaltungsbutler.de/docs/api/v1/
Swagger:  https://app.buchhaltungsbutler.de/docs/api/v1.de.json
"""

import os
import sys
import json
import base64
import httpx
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("buchhaltungsbutler")

API_BASE_URL = os.getenv(
    "BUCHHALTUNGSBUTLER_BASE_URL", "https://webapp.buchhaltungsbutler.de/api/v1"
)
API_CLIENT = os.getenv("BUCHHALTUNGSBUTLER_CLIENT", "")
API_SECRET = os.getenv("BUCHHALTUNGSBUTLER_SECRET", "")
API_KEY = os.getenv("BUCHHALTUNGSBUTLER_API_KEY", "")


def _auth_headers() -> dict:
    if not API_CLIENT or not API_SECRET:
        return {}
    credentials = base64.b64encode(
        f"{API_CLIENT}:{API_SECRET}".encode()
    ).decode()
    return {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }


def _api_post(endpoint: str, payload: dict) -> dict:
    """POST to BuchhaltungsButler API. All endpoints use POST with api_key in body."""
    url = f"{API_BASE_URL}/{endpoint}"
    payload = {**payload, "api_key": API_KEY}
    r = httpx.post(url, headers=_auth_headers(), json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def _ok(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def _err(e: Exception) -> str:
    return f"Error: {e}"

from functools import wraps

def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            return _err(e)
    return wrapper


# ═══════════════════════════════════════════════════════════════
# 3.1 ACCOUNTS
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
@handle_errors
async def bb_list_accounts() -> str:
    """List all accounts (Konten)."""
    return _ok(_api_post("accounts/get", {}))


@mcp.tool()
@handle_errors
async def bb_add_account(
    type: str,
    name: str,
    postingaccount_number: int,
    receipt_creates_transaction: bool = False,
    is_revision_safe: bool = False,
) -> str:
    """Add a new account (Konto). type: 'cash', 'bank/institution', or 'other'. Required: type, name, postingaccount_number."""
    payload = {
        "type": type,
        "name": name,
        "postingaccount_number": postingaccount_number,
        "receipt_creates_transaction": receipt_creates_transaction,
        "is_revision_safe": is_revision_safe,
    }
    return _ok(_api_post("accounts/add", payload))


# ═══════════════════════════════════════════════════════════════
# 3.2 COMMENTS
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
@handle_errors
async def bb_add_comment(
    comment_text: str,
    receipt_id_by_customer: str = "",
    transaction_id_by_customer: str = "",
) -> str:
    """Add a comment to a receipt or transaction. Specify exactly one of receipt_id_by_customer or transaction_id_by_customer."""
    payload = {"comment_text": comment_text}
    if receipt_id_by_customer:
        payload["receipt_id_by_customer"] = receipt_id_by_customer
    if transaction_id_by_customer:
        payload["transaction_id_by_customer"] = transaction_id_by_customer
    return _ok(_api_post("comments/add", payload))


# ═══════════════════════════════════════════════════════════════
# 3.3 COST LOCATIONS
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
@handle_errors
async def bb_list_cost_locations(
    code: str = "",
    limit: int = 1000,
    offset: int = 0,
) -> str:
    """List cost locations (Kostenstellen). Optionally filter by code."""
    payload: dict = {"limit": limit, "offset": offset}
    if code:
        payload["code"] = code
    return _ok(_api_post("cost-locations/get", payload))


@mcp.tool()
@handle_errors
async def bb_add_cost_location(code: str, name: str) -> str:
    """Add a new cost location (Kostenstelle). Required: code, name."""
    return _ok(_api_post("cost-locations/add", {"code": code, "name": name}))


@mcp.tool()
@handle_errors
async def bb_update_cost_location(code: str, name: str) -> str:
    """Update a cost location's name. Required: code, name."""
    return _ok(_api_post("cost-locations/update", {"code": code, "name": name}))


@mcp.tool()
@handle_errors
async def bb_delete_cost_location(code: str) -> str:
    """Delete a cost location by code. Required: code."""
    return _ok(_api_post("cost-locations/delete", {"code": code}))


# ═══════════════════════════════════════════════════════════════
# 3.4 INVOICES
# ═══════════════════════════════════════════════════════════════

def _build_invoice_payload(
    type: str,
    company_name: str,
    item_name: list,
    item_amount: list,
    item_single_price: list,
    item_vat: list,
    show_prices_type: str = "gross",
    date: str = "",
    item_unit: Optional[list] = None,
    item_description: Optional[list] = None,
    contact_person_name: str = "",
    street: str = "",
    additional_addressline: str = "",
    zip: str = "",
    city: str = "",
    country: str = "DE",
    email: str = "",
    invoicenumber: str = "",
    correspondence: str = "",
    discount_type: str = "",
    discount_value: str = "",
    payment_conditions: str = "",
    due_days: str = "",
    final_provisions: str = "",
    show_bankdata: bool = False,
    show_contactdata: bool = False,
    recurring_interval: str = "",
    recurring_date_next: str = "",
    date_of_supply: str = "",
    customer_number: str = "",
    payment_reference: str = "",
) -> dict:
    """Build the common invoice payload."""
    payload: dict = {
        "type": type,
        "show_prices_type": show_prices_type,
        "company_name": company_name,
        "date": date,
        "item_name": item_name,
        "item_amount": item_amount,
        "item_single_price": item_single_price,
        "item_vat": item_vat,
        "show_bankdata": show_bankdata,
        "show_contactdata": show_contactdata,
    }
    optional_fields = {
        "item_unit": item_unit,
        "item_description": item_description,
        "contact_person_name": contact_person_name,
        "street": street,
        "additional_addressline": additional_addressline,
        "zip": zip,
        "city": city,
        "country": country,
        "email": email,
        "invoicenumber": invoicenumber,
        "correspondence": correspondence,
        "discount_type": discount_type,
        "discount_value": discount_value,
        "payment_conditions": payment_conditions,
        "due_days": due_days,
        "final_provisions": final_provisions,
        "recurring_interval": recurring_interval,
        "recurring_date_next": recurring_date_next,
        "date_of_supply": date_of_supply,
        "customer_number": customer_number,
        "payment_reference": payment_reference,
    }
    payload.update({k: v for k, v in optional_fields.items() if v})
    return payload


@mcp.tool()
@handle_errors
async def bb_create_invoice(
    type: str,
    company_name: str,
    item_name: list,
    item_amount: list,
    item_single_price: list,
    item_vat: list,
    show_prices_type: str = "gross",
    date: str = "",
    item_unit: Optional[list] = None,
    item_description: Optional[list] = None,
    contact_person_name: str = "",
    street: str = "",
    additional_addressline: str = "",
    zip: str = "",
    city: str = "",
    country: str = "DE",
    email: str = "",
    invoicenumber: str = "",
    correspondence: str = "",
    discount_type: str = "",
    discount_value: str = "",
    payment_conditions: str = "",
    due_days: str = "",
    final_provisions: str = "",
    show_bankdata: bool = False,
    show_contactdata: bool = False,
    recurring_interval: str = "",
    recurring_date_next: str = "",
    date_of_supply: str = "",
    customer_number: str = "",
    payment_reference: str = "",
) -> str:
    """Create an invoice (Rechnung). type: 'invoice', 'credit', or 'offer'. show_prices_type: 'net' or 'gross'."""
    payload = _build_invoice_payload(**locals())
    return _ok(_api_post("invoices/create", payload))


@mcp.tool()
@handle_errors
async def bb_create_invoice_draft(
    type: str,
    company_name: str,
    item_name: list,
    item_amount: list,
    item_single_price: list,
    item_vat: list,
    show_prices_type: str = "gross",
    date: str = "",
    item_unit: Optional[list] = None,
    item_description: Optional[list] = None,
    contact_person_name: str = "",
    street: str = "",
    additional_addressline: str = "",
    zip: str = "",
    city: str = "",
    country: str = "DE",
    email: str = "",
    correspondence: str = "",
    discount_type: str = "",
    discount_value: str = "",
    payment_conditions: str = "",
    final_provisions: str = "",
    show_bankdata: bool = False,
    show_contactdata: bool = False,
    recurring_interval: str = "",
    recurring_date_next: str = "",
    date_of_supply: str = "",
    customer_number: str = "",
) -> str:
    """Create an invoice draft (Entwurf). Same params as bb_create_invoice but without invoicenumber/payment_reference/due_days."""
    payload = _build_invoice_payload(**locals())
    return _ok(_api_post("invoices/create/draft", payload))


@mcp.tool()
@handle_errors
async def bb_create_einvoice(
    type: str,
    company_name: str,
    item_name: list,
    item_amount: list,
    item_single_price: list,
    item_tax_type: list,
    e_invoice_id: str,
    street: str,
    zip: str,
    city: str,
    country: str,
    email: str,
    show_prices_type: str = "gross",
    date: str = "",
    item_tax_amount: Optional[list] = None,
    item_unit: Optional[list] = None,
    item_description: Optional[list] = None,
    contact_person_name: str = "",
    additional_addressline: str = "",
    invoicenumber: str = "",
    correspondence: str = "",
    discount_type: str = "",
    discount_value: str = "",
    payment_conditions: str = "",
    due_days: str = "",
    final_provisions: str = "",
    show_bankdata: bool = False,
    show_contactdata: bool = False,
    recurring_interval: str = "",
    recurring_date_next: str = "",
    date_of_supply: str = "",
    customer_number: str = "",
    payment_reference: str = "",
) -> str:
    """Create an e-invoice (E-Rechnung). Requires e_invoice_id (buyer reference) and full address. item_tax_type: 'S','Z','AE','K','G','E'."""
    payload: dict = {
        "type": type,
        "show_prices_type": show_prices_type,
        "company_name": company_name,
        "date": date,
        "item_name": item_name,
        "item_amount": item_amount,
        "item_single_price": item_single_price,
        "item_tax_type": item_tax_type,
        "e_invoice_id": e_invoice_id,
        "street": street,
        "zip": zip,
        "city": city,
        "country": country,
        "email": email,
        "show_bankdata": show_bankdata,
        "show_contactdata": show_contactdata,
    }
    optional_fields = {
        "item_tax_amount": item_tax_amount,
        "item_unit": item_unit,
        "item_description": item_description,
        "contact_person_name": contact_person_name,
        "additional_addressline": additional_addressline,
        "invoicenumber": invoicenumber,
        "correspondence": correspondence,
        "discount_type": discount_type,
        "discount_value": discount_value,
        "payment_conditions": payment_conditions,
        "due_days": due_days,
        "final_provisions": final_provisions,
        "recurring_interval": recurring_interval,
        "recurring_date_next": recurring_date_next,
        "date_of_supply": date_of_supply,
        "customer_number": customer_number,
        "payment_reference": payment_reference,
    }
    payload.update({k: v for k, v in optional_fields.items() if v})
    return _ok(_api_post("invoices/create/e-invoice", payload))


# ═══════════════════════════════════════════════════════════════
# 3.5 POSTINGS
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
@handle_errors
async def bb_list_postings(
    date_from: str = "2025-01-01",
    date_to: str = "2025-12-31",
    limit: int = 500,
    offset: int = 0,
    account: str = "",
    postingaccount: str = "",
    posting_status: str = "",
    cost_location: str = "",
    date_last_action_from: str = "",
    date_last_action_to: str = "",
    order: str = "",
) -> str:
    """List all postings (Buchungssätze). date_from and date_to are both required (default: full year 2025). order: 'default', 'date ASC', 'date DESC', 'date_last_action ASC', 'date_last_action DESC', 'id_by_customer ASC', 'id_by_customer DESC'."""
    payload: dict = {"limit": limit, "offset": offset, "date_from": date_from, "date_to": date_to}
    if account:
        payload["account"] = account
    if postingaccount:
        payload["postingaccount"] = postingaccount
    if posting_status:
        payload["posting_status"] = posting_status
    if cost_location:
        payload["cost_location"] = cost_location
    if date_last_action_from:
        payload["date_last_action_from"] = date_last_action_from
    if date_last_action_to:
        payload["date_last_action_to"] = date_last_action_to
    if order:
        payload["order"] = order
    return _ok(_api_post("postings/get", payload))


@mcp.tool()
@handle_errors
async def bb_create_posting(
    posting_type: str = "free",
    account: str = "",
    amount: float = 0.0,
    postingaccount: str = "",
    date: str = "",
    cost_location: str = "",
    cost_location_two: str = "",
    receipt_id_by_customer: str = "",
    transaction_id_by_customer: str = "",
) -> str:
    """Create a posting (Buchungssatz). posting_type: 'free', 'receipt', or 'transaction'."""
    if posting_type == "receipt" and receipt_id_by_customer:
        endpoint = "postings/add/receipt"
        payload: dict = {
            "receipt_id_by_customer": receipt_id_by_customer,
            "postings": [{
                "account": account,
                "amount": amount,
                "postingaccount": postingaccount,
            }],
        }
    elif posting_type == "transaction" and transaction_id_by_customer:
        endpoint = "postings/add/transaction"
        payload = {
            "transaction_id_by_customer": transaction_id_by_customer,
            "postings": [{
                "account": account,
                "amount": amount,
                "postingaccount": postingaccount,
            }],
        }
    else:
        endpoint = "postings/add/free"
        payload = {
            "account": account,
            "amount": amount,
            "postingaccount": postingaccount,
            "date": date or None,
        }
    if cost_location:
        payload["cost_location"] = cost_location
    if cost_location_two:
        payload["cost_location_two"] = cost_location_two
    return _ok(_api_post(endpoint, payload))


@mcp.tool()
@handle_errors
async def bb_create_postings_batch_free(free_postings: list) -> str:
    """Create multiple free postings in batch. free_postings is a list of dicts with keys: account, amount, postingaccount, date (opt), cost_location (opt), cost_location_two (opt)."""
    return _ok(_api_post("postings/add-batch/free", {"free_postings": free_postings}))


@mcp.tool()
@handle_errors
async def bb_create_postings_batch_receipts(receipt_postings: list) -> str:
    """Create multiple receipt postings in batch. receipt_postings is a list of dicts with keys: receipt_id_by_customer, postings (list of {account, amount, postingaccount}), cost_locations (opt), cost_locations_two (opt)."""
    return _ok(_api_post("postings/add-batch/receipts", {"receipt_postings": receipt_postings}))


@mcp.tool()
@handle_errors
async def bb_create_postings_batch_transactions(transaction_postings: list) -> str:
    """Create multiple transaction postings in batch. transaction_postings is a list of dicts with keys: transaction_id_by_customer, postings (list of {account, amount, postingaccount}), cost_locations (opt), cost_locations_two (opt)."""
    return _ok(_api_post("postings/add-batch/transactions", {"transaction_postings": transaction_postings}))


@mcp.tool()
@handle_errors
async def bb_assign_receipt_to_free_posting(
    receipt_id_by_customer: int,
    posting_id_by_customer: int,
) -> str:
    """Assign a receipt to a free posting. Required: receipt_id_by_customer, posting_id_by_customer."""
    return _ok(_api_post("postings/assign/receipt-to-free-posting", {
        "receipt_id_by_customer": receipt_id_by_customer,
        "posting_id_by_customer": posting_id_by_customer,
    }))


@mcp.tool()
@handle_errors
async def bb_unconfirm_free_posting(posting_id_by_customer: int) -> str:
    """Unconfirm (delete) a free posting by its customer ID. Required: posting_id_by_customer."""
    return _ok(_api_post("postings/unconfirm/free", {"posting_id_by_customer": posting_id_by_customer}))


@mcp.tool()
@handle_errors
async def bb_unconfirm_receipt_posting(receipt_id_by_customer: int) -> str:
    """Unconfirm (delete) all postings for a receipt. Required: receipt_id_by_customer."""
    return _ok(_api_post("postings/unconfirm/receipt", {
        "receipt_id_by_customer": receipt_id_by_customer,
    }))


@mcp.tool()
@handle_errors
async def bb_unconfirm_transaction_posting(transaction_id_by_customer: int) -> str:
    """Unconfirm (delete) all postings for a transaction. Required: transaction_id_by_customer."""
    return _ok(_api_post("postings/unconfirm/transaction", {
        "transaction_id_by_customer": transaction_id_by_customer,
    }))


# ═══════════════════════════════════════════════════════════════
# 3.6 RECEIPTS (BELEGE)
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
@handle_errors
async def bb_list_receipts(
    list_direction: str = "inbound",
    date_from: str = "",
    date_to: str = "",
    limit: int = 500,
    offset: int = 0,
    payment_status: str = "",
    counterparty: str = "",
    include_offers: bool = False,
    deleted: bool = False,
    invoicenumber: str = "",
    due_date: str = "",
    order: str = "",
) -> str:
    """List receipts (Belege). list_direction: 'inbound' (Eingang) or 'outbound' (Ausgang/Rechnungen)."""
    payload: dict = {
        "list_direction": list_direction,
        "limit": limit,
        "offset": offset,
        "include_offers": include_offers,
        "deleted": deleted,
    }
    if date_from:
        payload["date_from"] = date_from
    if date_to:
        payload["date_to"] = date_to
    if payment_status:
        payload["payment_status"] = payment_status
    if counterparty:
        payload["counterparty"] = counterparty
    if invoicenumber:
        payload["invoicenumber"] = invoicenumber
    if due_date:
        payload["due_date"] = due_date
    if order:
        payload["order"] = order
    return _ok(_api_post("receipts/get", payload))


@mcp.tool()
@handle_errors
async def bb_get_receipt(
    receipt_id_by_customer: str,
    get_file: bool = False,
) -> str:
    """Get a single receipt by its customer ID. Set get_file=True to also receive the base64-encoded file."""
    payload: dict = {"receipt_id_by_customer": receipt_id_by_customer}
    if get_file:
        payload["get_file"] = True
    return _ok(_api_post("receipts/get/id_by_customer", payload))


@mcp.tool()
@handle_errors
async def bb_upload_receipt(
    filename: str,
    file_base64: str,
    list_direction: str = "inbound",
    account: int = 0,
    creditor_debtor: int = 0,
    counterparty: str = "",
    invoice_number: str = "",
    date: str = "",
    amount: float = 0.0,
    currency: str = "EUR",
    vat_rate: float = 0.0,
    payment_reference: str = "",
    date_delivery: str = "",
    date_payment_due: str = "",
    link_to_receipt_id_by_customer: int = 0,
) -> str:
    """Upload a receipt (PDF/image). file_base64 must be base64-encoded file content. Supports optional metadata."""
    payload: dict = {
        "filename": filename,
        "file": file_base64,
        "list_direction": list_direction,
    }
    if account:
        payload["account"] = account
    if creditor_debtor:
        payload["creditor_debtor"] = creditor_debtor
    if counterparty:
        payload["counterparty"] = counterparty
    if invoice_number:
        payload["invoice_number"] = invoice_number
    if date:
        payload["date"] = date
    if amount:
        payload["amount"] = amount
    if currency:
        payload["currency"] = currency
    if vat_rate:
        payload["vat_rate"] = vat_rate
    if payment_reference:
        payload["payment_reference"] = payment_reference
    if date_delivery:
        payload["date_delivery"] = date_delivery
    if date_payment_due:
        payload["date_payment_due"] = date_payment_due
    if link_to_receipt_id_by_customer:
        payload["link_to_receipt_id_by_customer"] = link_to_receipt_id_by_customer
    return _ok(_api_post("receipts/upload", payload))


@mcp.tool()
@handle_errors
async def bb_add_receipt(
    type: str,
    counterparty: str,
    invoice_number: str,
    date: str,
    amount: float,
    currency: str = "EUR",
    vat_rate: float = 0.0,
    account: int = 0,
    creditor_debtor: int = 0,
    payment_reference: str = "",
    date_delivery: str = "",
    date_payment_due: str = "",
    link_to_receipt_id_by_customer: int = 0,
) -> str:
    """Create a receipt entry without uploading a file. Required: type ('invoice inbound'/'invoice outbound'/'credit inbound'/'credit outbound'), counterparty, invoice_number, date (YYYY-MM-DD), amount."""
    payload: dict = {
        "type": type,
        "counterparty": counterparty,
        "invoice_number": invoice_number,
        "date": date,
        "amount": amount,
        "currency": currency,
    }
    if vat_rate:
        payload["vat_rate"] = vat_rate
    if account:
        payload["account"] = account
    if creditor_debtor:
        payload["creditor_debtor"] = creditor_debtor
    if payment_reference:
        payload["payment_reference"] = payment_reference
    if date_delivery:
        payload["date_delivery"] = date_delivery
    if date_payment_due:
        payload["date_payment_due"] = date_payment_due
    if link_to_receipt_id_by_customer:
        payload["link_to_receipt_id_by_customer"] = link_to_receipt_id_by_customer
    return _ok(_api_post("receipts/add", payload))


@mcp.tool()
@handle_errors
async def bb_add_receipts_batch(receipts: list) -> str:
    """Add multiple receipts in batch. receipts is a list of dicts with the same keys as bb_add_receipt."""
    return _ok(_api_post("receipts/addBatch", {"receipts": receipts}))


@mcp.tool()
@handle_errors
async def bb_get_assigned_transactions(
    receipt_id_by_customer: str,
    confirmed_only: bool = False,
) -> str:
    """Get transactions assigned to a receipt."""
    payload: dict = {"receipt_id_by_customer": receipt_id_by_customer}
    if confirmed_only:
        payload["confirmed_only"] = True
    return _ok(_api_post("receipts/assigned-transactions/get", payload))


@mcp.tool()
@handle_errors
async def bb_delete_receipt(receipt_id_by_customer: str) -> str:
    """Delete a receipt by its customer ID."""
    return _ok(_api_post("receipts/delete/id_by_customer", {
        "receipt_id_by_customer": receipt_id_by_customer
    }))


@mcp.tool()
@handle_errors
async def bb_restore_receipt(receipt_id_by_customer: str) -> str:
    """Restore a previously deleted receipt."""
    return _ok(_api_post("receipts/restore/id_by_customer", {
        "receipt_id_by_customer": receipt_id_by_customer
    }))


# ═══════════════════════════════════════════════════════════════
# 3.7 SETTINGS
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
@handle_errors
async def bb_list_debtors(limit: int = 500, offset: int = 0) -> str:
    """List all debtors (Debitoren / Kunden)."""
    return _ok(_api_post("settings/get/debtors", {"limit": limit, "offset": offset}))


@mcp.tool()
@handle_errors
async def bb_list_creditors(limit: int = 500, offset: int = 0) -> str:
    """List all creditors (Kreditoren / Lieferanten)."""
    return _ok(_api_post("settings/get/creditors", {"limit": limit, "offset": offset}))


@mcp.tool()
@handle_errors
async def bb_list_postingaccounts(
    limit: int = 500,
    offset: int = 0,
    order: str = "",
    exclude_postingaccounts: bool = False,
    exclude_accounts: bool = False,
    exclude_creditors: bool = False,
    exclude_debtors: bool = False,
) -> str:
    """List all posting accounts (Buchungskonten). Supports filtering and ordering."""
    payload: dict = {"limit": limit, "offset": offset}
    if order:
        payload["order"] = order
    if exclude_postingaccounts:
        payload["exclude_postingaccounts"] = True
    if exclude_accounts:
        payload["exclude_accounts"] = True
    if exclude_creditors:
        payload["exclude_creditors"] = True
    if exclude_debtors:
        payload["exclude_debtors"] = True
    return _ok(_api_post("settings/get/postingaccounts", payload))


def _build_contact_payload(
    name: str = "",
    contact_person_name: str = "",
    street: str = "",
    additional_address_line: str = "",
    zip: str = "",
    city: str = "",
    country: str = "DE",
    sales_tax_id: str = "",
    email: str = "",
    iban: str = "",
    bic: str = "",
    postingaccount_number: str = "",
    due_in_days: int = 0,
    customer_number: str = "",
) -> dict:
    """Build common payload for creditor/debtor operations."""
    optional_fields = {
        "name": name,
        "contact_person_name": contact_person_name,
        "street": street,
        "additional_address_line": additional_address_line,
        "zip": zip,
        "city": city,
        "country": country,
        "sales_tax_id": sales_tax_id,
        "email": email,
        "iban": iban,
        "bic": bic,
        "postingaccount_number": postingaccount_number,
        "due_in_days": due_in_days,
        "customer_number": customer_number,
    }
    return {k: v for k, v in optional_fields.items() if v}


@mcp.tool()
@handle_errors
async def bb_add_creditor(
    name: str = "",
    contact_person_name: str = "",
    street: str = "",
    additional_address_line: str = "",
    zip: str = "",
    city: str = "",
    country: str = "DE",
    sales_tax_id: str = "",
    email: str = "",
    iban: str = "",
    bic: str = "",
    postingaccount_number: str = "",
    due_in_days: int = 0,
) -> str:
    """Add a new creditor (Kreditor / Lieferant)."""
    payload = _build_contact_payload(**locals())
    return _ok(_api_post("settings/add/creditor", payload))


@mcp.tool()
@handle_errors
async def bb_add_debtor(
    name: str = "",
    contact_person_name: str = "",
    street: str = "",
    additional_address_line: str = "",
    customer_number: str = "",
    zip: str = "",
    city: str = "",
    country: str = "DE",
    sales_tax_id: str = "",
    email: str = "",
    iban: str = "",
    bic: str = "",
    postingaccount_number: str = "",
) -> str:
    """Add a new debtor (Debitor / Kunde)."""
    payload = _build_contact_payload(**locals())
    return _ok(_api_post("settings/add/debtor", payload))


@mcp.tool()
@handle_errors
async def bb_add_creditors_batch(creditors: list) -> str:
    """Add multiple creditors in batch. Each dict uses the same keys as bb_add_creditor."""
    return _ok(_api_post("settings/add-batch/creditors", {"creditors": creditors}))


@mcp.tool()
@handle_errors
async def bb_add_debtors_batch(debtors: list) -> str:
    """Add multiple debtors in batch. Each dict uses the same keys as bb_add_debtor."""
    return _ok(_api_post("settings/add-batch/debtors", {"debtors": debtors}))


@mcp.tool()
@handle_errors
async def bb_add_postingaccount(
    number: str = "",
    name: str = "",
    type: str = "",
) -> str:
    """Add a new posting account (Buchungskonto)."""
    optional_fields = {
        "number": number,
        "name": name,
        "type": type,
    }
    payload = {k: v for k, v in optional_fields.items() if v}
    return _ok(_api_post("settings/add/postingaccount", payload))


@mcp.tool()
@handle_errors
async def bb_update_creditor(
    name: str = "",
    contact_person_name: str = "",
    street: str = "",
    additional_address_line: str = "",
    zip: str = "",
    city: str = "",
    country: str = "DE",
    sales_tax_id: str = "",
    email: str = "",
    iban: str = "",
    bic: str = "",
    due_in_days: int = 0,
) -> str:
    """Update an existing creditor (Kreditor)."""
    payload = _build_contact_payload(**locals())
    return _ok(_api_post("settings/update/creditor", payload))


@mcp.tool()
@handle_errors
async def bb_update_debtor(
    name: str = "",
    contact_person_name: str = "",
    street: str = "",
    additional_address_line: str = "",
    customer_number: str = "",
    zip: str = "",
    city: str = "",
    country: str = "DE",
    sales_tax_id: str = "",
    email: str = "",
    iban: str = "",
    bic: str = "",
) -> str:
    """Update an existing debtor (Debitor)."""
    payload = _build_contact_payload(**locals())
    return _ok(_api_post("settings/update/debtor", payload))


@mcp.tool()
@handle_errors
async def bb_update_postingaccount(
    number: str = "",
    name: str = "",
    type: str = "",
) -> str:
    """Update an existing posting account (Buchungskonto)."""
    optional_fields = {
        "number": number,
        "name": name,
        "type": type,
    }
    payload = {k: v for k, v in optional_fields.items() if v}
    return _ok(_api_post("settings/update/postingaccount", payload))


# ═══════════════════════════════════════════════════════════════
# 3.8 TRANSACTIONS
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
@handle_errors
async def bb_list_transactions(
    id_by_customer_from: int = 0,
    id_by_customer_to: int = 0,
    date_from: str = "",
    date_to: str = "",
    account: int = 0,
    to_from: str = "",
    limit: int = 500,
    offset: int = 0,
) -> str:
    """List transactions (Bank transactions / Umsätze)."""
    payload: dict = {"limit": limit, "offset": offset}
    optional_fields = {
        "id_by_customer_from": id_by_customer_from,
        "id_by_customer_to": id_by_customer_to,
        "date_from": date_from,
        "date_to": date_to,
        "account": account,
        "to_from": to_from,
    }
    payload.update({k: v for k, v in optional_fields.items() if v})
    return _ok(_api_post("transactions/get", payload))


@mcp.tool()
@handle_errors
async def bb_get_transaction(id_by_customer: str) -> str:
    """Get a single transaction by its customer ID."""
    return _ok(_api_post("transactions/get/id_by_customer", {
        "id_by_customer": id_by_customer
    }))


@mcp.tool()
@handle_errors
async def bb_add_transaction(
    value_date: str,
    account_number: str,
    bank_code: str = "",
    bank_name: str = "",
    purpose: str = "",
    type: str = "",
    booking_text: str = "",
    payment_reference: str = "",
    currency: str = "EUR",
) -> str:
    """Add a new transaction (Bank transaction / Umsatz)."""
    payload: dict = {
        "value_date": value_date,
        "account_number": account_number,
        "currency": currency,
    }
    optional_fields = {
        "bank_code": bank_code,
        "bank_name": bank_name,
        "purpose": purpose,
        "type": type,
        "booking_text": booking_text,
        "payment_reference": payment_reference,
    }
    payload.update({k: v for k, v in optional_fields.items() if v})
    return _ok(_api_post("transactions/add", payload))


@mcp.tool()
@handle_errors
async def bb_add_transactions_batch(transactions: list) -> str:
    """Add multiple transactions in batch. Each dict uses the same keys as bb_add_transaction."""
    return _ok(_api_post("transactions/addBatch", {"transactions": transactions}))


@mcp.tool()
@handle_errors
async def bb_assign_receipt_to_transaction(
    receipt_id_by_customer: str,
    transaction_id_by_customer: str,
) -> str:
    """Assign a receipt to a transaction."""
    return _ok(_api_post("transactions/assign/receipt", {
        "receipt_id_by_customer": receipt_id_by_customer,
        "transaction_id_by_customer": transaction_id_by_customer,
    }))


@mcp.tool()
@handle_errors
async def bb_assign_receipts_to_transactions_batch(assignments: list) -> str:
    """Assign multiple receipts to transactions in batch. Each dict has: receipt_id_by_customer, transaction_id_by_customer."""
    return _ok(_api_post("transactions/assign-batch/receipt", {"assignments": assignments}))


@mcp.tool()
@handle_errors
async def bb_get_assigned_receipts(
    transaction_id_by_customer: str,
    confirmed_only: bool = False,
) -> str:
    """Get receipts assigned to a transaction."""
    payload: dict = {"transaction_id_by_customer": transaction_id_by_customer}
    if confirmed_only:
        payload["confirmed_only"] = True
    return _ok(_api_post("transactions/assigned-receipts/get", payload))


@mcp.tool()
@handle_errors
async def bb_unassign_receipt_from_transaction(
    receipt_id_by_customer: str,
    transaction_id_by_customer: str,
) -> str:
    """Unassign a receipt from a transaction."""
    return _ok(_api_post("transactions/unassign/receipt", {
        "receipt_id_by_customer": receipt_id_by_customer,
        "transaction_id_by_customer": transaction_id_by_customer,
    }))


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request

    if "--transport" in sys.argv and "stdio" in sys.argv:
        mcp.run()
    else:
        class FixHostMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                request.scope["headers"] = [
                    (b"host", b"localhost:8000") if k == b"host" else (k, v)
                    for k, v in request.scope["headers"]
                ]
                return await call_next(request)

        app = mcp.sse_app()
        app.add_middleware(FixHostMiddleware)
        uvicorn.run(app, host="0.0.0.0", port=8000)
