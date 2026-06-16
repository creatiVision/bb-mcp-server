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


# ═══════════════════════════════════════════════════════════════
# 3.1 ACCOUNTS
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
async def bb_list_accounts() -> str:
    """List all accounts (Konten)."""
    try:
        return _ok(_api_post("accounts/get", {}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_add_account(
    type: str,
    name: str,
    postingaccount_number: int,
    receipt_creates_transaction: bool = False,
    is_revision_safe: bool = False,
) -> str:
    """Add a new account (Konto). type: 'cash', 'bank/institution', or 'other'. Required: type, name, postingaccount_number."""
    try:
        payload = {
            "type": type,
            "name": name,
            "postingaccount_number": postingaccount_number,
            "receipt_creates_transaction": receipt_creates_transaction,
            "is_revision_safe": is_revision_safe,
        }
        return _ok(_api_post("accounts/add", payload))
    except Exception as e:
        return _err(e)


# ═══════════════════════════════════════════════════════════════
# 3.2 COMMENTS
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
async def bb_add_comment(
    comment_text: str,
    receipt_id_by_customer: str = "",
    transaction_id_by_customer: str = "",
) -> str:
    """Add a comment to a receipt or transaction. Specify exactly one of receipt_id_by_customer or transaction_id_by_customer."""
    try:
        payload = {"comment_text": comment_text}
        if receipt_id_by_customer:
            payload["receipt_id_by_customer"] = receipt_id_by_customer
        if transaction_id_by_customer:
            payload["transaction_id_by_customer"] = transaction_id_by_customer
        return _ok(_api_post("comments/add", payload))
    except Exception as e:
        return _err(e)


# ═══════════════════════════════════════════════════════════════
# 3.3 COST LOCATIONS
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
async def bb_list_cost_locations(
    code: str = "",
    limit: int = 1000,
    offset: int = 0,
) -> str:
    """List cost locations (Kostenstellen). Optionally filter by code."""
    try:
        payload: dict = {"limit": limit, "offset": offset}
        if code:
            payload["code"] = code
        return _ok(_api_post("cost-locations/get", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_add_cost_location(code: str, name: str) -> str:
    """Add a new cost location (Kostenstelle). Required: code, name."""
    try:
        return _ok(_api_post("cost-locations/add", {"code": code, "name": name}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_update_cost_location(code: str, name: str) -> str:
    """Update a cost location's name. Required: code, name."""
    try:
        return _ok(_api_post("cost-locations/update", {"code": code, "name": name}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_delete_cost_location(code: str) -> str:
    """Delete a cost location by code. Required: code."""
    try:
        return _ok(_api_post("cost-locations/delete", {"code": code}))
    except Exception as e:
        return _err(e)


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
    if item_unit:
        payload["item_unit"] = item_unit
    if item_description:
        payload["item_description"] = item_description
    if contact_person_name:
        payload["contact_person_name"] = contact_person_name
    if street:
        payload["street"] = street
    if additional_addressline:
        payload["additional_addressline"] = additional_addressline
    if zip:
        payload["zip"] = zip
    if city:
        payload["city"] = city
    if country:
        payload["country"] = country
    if email:
        payload["email"] = email
    if invoicenumber:
        payload["invoicenumber"] = invoicenumber
    if correspondence:
        payload["correspondence"] = correspondence
    if discount_type:
        payload["discount_type"] = discount_type
    if discount_value:
        payload["discount_value"] = discount_value
    if payment_conditions:
        payload["payment_conditions"] = payment_conditions
    if due_days:
        payload["due_days"] = due_days
    if final_provisions:
        payload["final_provisions"] = final_provisions
    if recurring_interval:
        payload["recurring_interval"] = recurring_interval
    if recurring_date_next:
        payload["recurring_date_next"] = recurring_date_next
    if date_of_supply:
        payload["date_of_supply"] = date_of_supply
    if customer_number:
        payload["customer_number"] = customer_number
    if payment_reference:
        payload["payment_reference"] = payment_reference
    return payload


@mcp.tool()
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
    try:
        payload = _build_invoice_payload(**locals())
        return _ok(_api_post("invoices/create", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
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
    try:
        payload = _build_invoice_payload(**locals())
        return _ok(_api_post("invoices/create/draft", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
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
    try:
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
        if item_tax_amount:
            payload["item_tax_amount"] = item_tax_amount
        if item_unit:
            payload["item_unit"] = item_unit
        if item_description:
            payload["item_description"] = item_description
        if contact_person_name:
            payload["contact_person_name"] = contact_person_name
        if additional_addressline:
            payload["additional_addressline"] = additional_addressline
        if invoicenumber:
            payload["invoicenumber"] = invoicenumber
        if correspondence:
            payload["correspondence"] = correspondence
        if discount_type:
            payload["discount_type"] = discount_type
        if discount_value:
            payload["discount_value"] = discount_value
        if payment_conditions:
            payload["payment_conditions"] = payment_conditions
        if due_days:
            payload["due_days"] = due_days
        if final_provisions:
            payload["final_provisions"] = final_provisions
        if recurring_interval:
            payload["recurring_interval"] = recurring_interval
        if recurring_date_next:
            payload["recurring_date_next"] = recurring_date_next
        if date_of_supply:
            payload["date_of_supply"] = date_of_supply
        if customer_number:
            payload["customer_number"] = customer_number
        if payment_reference:
            payload["payment_reference"] = payment_reference
        return _ok(_api_post("invoices/create/e-invoice", payload))
    except Exception as e:
        return _err(e)


# ═══════════════════════════════════════════════════════════════
# 3.5 POSTINGS
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
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
    try:
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
    except Exception as e:
        return _err(e)


@mcp.tool()
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
    try:
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
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_create_postings_batch_free(free_postings: list) -> str:
    """Create multiple free postings in batch. free_postings is a list of dicts with keys: account, amount, postingaccount, date (opt), cost_location (opt), cost_location_two (opt)."""
    try:
        return _ok(_api_post("postings/add-batch/free", {"free_postings": free_postings}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_create_postings_batch_receipts(receipt_postings: list) -> str:
    """Create multiple receipt postings in batch. receipt_postings is a list of dicts with keys: receipt_id_by_customer, postings (list of {account, amount, postingaccount}), cost_locations (opt), cost_locations_two (opt)."""
    try:
        return _ok(_api_post("postings/add-batch/receipts", {"receipt_postings": receipt_postings}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_create_postings_batch_transactions(transaction_postings: list) -> str:
    """Create multiple transaction postings in batch. transaction_postings is a list of dicts with keys: transaction_id_by_customer, postings (list of {account, amount, postingaccount}), cost_locations (opt), cost_locations_two (opt)."""
    try:
        return _ok(_api_post("postings/add-batch/transactions", {"transaction_postings": transaction_postings}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_assign_receipt_to_free_posting(
    receipt_id_by_customer: int,
    posting_id_by_customer: int,
) -> str:
    """Assign a receipt to a free posting. Required: receipt_id_by_customer, posting_id_by_customer."""
    try:
        return _ok(_api_post("postings/assign/receipt-to-free-posting", {
            "receipt_id_by_customer": receipt_id_by_customer,
            "posting_id_by_customer": posting_id_by_customer,
        }))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_unconfirm_free_posting(posting_id_by_customer: int) -> str:
    """Unconfirm (delete) a free posting by its customer ID. Required: posting_id_by_customer."""
    try:
        return _ok(_api_post("postings/unconfirm/free", {"posting_id_by_customer": posting_id_by_customer}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_unconfirm_receipt_posting(receipt_id_by_customer: int) -> str:
    """Unconfirm (delete) all postings for a receipt. Required: receipt_id_by_customer."""
    try:
        return _ok(_api_post("postings/unconfirm/receipt", {
            "receipt_id_by_customer": receipt_id_by_customer,
        }))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_unconfirm_transaction_posting(transaction_id_by_customer: int) -> str:
    """Unconfirm (delete) all postings for a transaction. Required: transaction_id_by_customer."""
    try:
        return _ok(_api_post("postings/unconfirm/transaction", {
            "transaction_id_by_customer": transaction_id_by_customer,
        }))
    except Exception as e:
        return _err(e)


# ═══════════════════════════════════════════════════════════════
# 3.6 RECEIPTS (BELEGE)
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
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
    try:
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
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_get_receipt(
    receipt_id_by_customer: str,
    get_file: bool = False,
) -> str:
    """Get a single receipt by its customer ID. Set get_file=True to also receive the base64-encoded file."""
    try:
        payload: dict = {"receipt_id_by_customer": receipt_id_by_customer}
        if get_file:
            payload["get_file"] = True
        return _ok(_api_post("receipts/get/id_by_customer", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
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
    try:
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
    except Exception as e:
        return _err(e)


@mcp.tool()
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
    try:
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
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_add_receipts_batch(receipts: list) -> str:
    """Add multiple receipts in batch. receipts is a list of dicts with the same keys as bb_add_receipt."""
    try:
        return _ok(_api_post("receipts/addBatch", {"receipts": receipts}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_get_assigned_transactions(
    receipt_id_by_customer: str,
    confirmed_only: bool = False,
) -> str:
    """Get transactions assigned to a receipt."""
    try:
        payload: dict = {"receipt_id_by_customer": receipt_id_by_customer}
        if confirmed_only:
            payload["confirmed_only"] = True
        return _ok(_api_post("receipts/assigned-transactions/get", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_delete_receipt(receipt_id_by_customer: str) -> str:
    """Delete a receipt by its customer ID."""
    try:
        return _ok(_api_post("receipts/delete/id_by_customer", {
            "receipt_id_by_customer": receipt_id_by_customer
        }))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_restore_receipt(receipt_id_by_customer: str) -> str:
    """Restore a previously deleted receipt."""
    try:
        return _ok(_api_post("receipts/restore/id_by_customer", {
            "receipt_id_by_customer": receipt_id_by_customer
        }))
    except Exception as e:
        return _err(e)


# ═══════════════════════════════════════════════════════════════
# 3.7 SETTINGS
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
async def bb_list_debtors(limit: int = 500, offset: int = 0) -> str:
    """List all debtors (Debitoren / Kunden)."""
    try:
        return _ok(_api_post("settings/get/debtors", {"limit": limit, "offset": offset}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_list_creditors(limit: int = 500, offset: int = 0) -> str:
    """List all creditors (Kreditoren / Lieferanten)."""
    try:
        return _ok(_api_post("settings/get/creditors", {"limit": limit, "offset": offset}))
    except Exception as e:
        return _err(e)


@mcp.tool()
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
    try:
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
    except Exception as e:
        return _err(e)


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
    payload: dict = {}
    if name:
        payload["name"] = name
    if contact_person_name:
        payload["contact_person_name"] = contact_person_name
    if street:
        payload["street"] = street
    if additional_address_line:
        payload["additional_address_line"] = additional_address_line
    if zip:
        payload["zip"] = zip
    if city:
        payload["city"] = city
    if country:
        payload["country"] = country
    if sales_tax_id:
        payload["sales_tax_id"] = sales_tax_id
    if email:
        payload["email"] = email
    if iban:
        payload["iban"] = iban
    if bic:
        payload["bic"] = bic
    if postingaccount_number:
        payload["postingaccount_number"] = postingaccount_number
    if due_in_days:
        payload["due_in_days"] = due_in_days
    if customer_number:
        payload["customer_number"] = customer_number
    return payload


@mcp.tool()
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
    try:
        payload = _build_contact_payload(**locals())
        return _ok(_api_post("settings/add/creditor", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
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
    try:
        payload = _build_contact_payload(**locals())
        return _ok(_api_post("settings/add/debtor", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_add_creditors_batch(creditors: list) -> str:
    """Add multiple creditors in batch. Each dict uses the same keys as bb_add_creditor."""
    try:
        return _ok(_api_post("settings/add-batch/creditors", {"creditors": creditors}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_add_debtors_batch(debtors: list) -> str:
    """Add multiple debtors in batch. Each dict uses the same keys as bb_add_debtor."""
    try:
        return _ok(_api_post("settings/add-batch/debtors", {"debtors": debtors}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_add_postingaccount(
    number: str = "",
    name: str = "",
    type: str = "",
) -> str:
    """Add a new posting account (Buchungskonto)."""
    try:
        payload: dict = {}
        if number:
            payload["number"] = number
        if name:
            payload["name"] = name
        if type:
            payload["type"] = type
        return _ok(_api_post("settings/add/postingaccount", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
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
    try:
        payload = _build_contact_payload(**locals())
        return _ok(_api_post("settings/update/creditor", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
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
    try:
        payload = _build_contact_payload(**locals())
        return _ok(_api_post("settings/update/debtor", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_update_postingaccount(
    number: str = "",
    name: str = "",
    type: str = "",
) -> str:
    """Update an existing posting account (Buchungskonto)."""
    try:
        payload: dict = {}
        if number:
            payload["number"] = number
        if name:
            payload["name"] = name
        if type:
            payload["type"] = type
        return _ok(_api_post("settings/update/postingaccount", payload))
    except Exception as e:
        return _err(e)


# ═══════════════════════════════════════════════════════════════
# 3.8 TRANSACTIONS
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
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
    try:
        payload: dict = {"limit": limit, "offset": offset}
        if id_by_customer_from:
            payload["id_by_customer_from"] = id_by_customer_from
        if id_by_customer_to:
            payload["id_by_customer_to"] = id_by_customer_to
        if date_from:
            payload["date_from"] = date_from
        if date_to:
            payload["date_to"] = date_to
        if account:
            payload["account"] = account
        if to_from:
            payload["to_from"] = to_from
        return _ok(_api_post("transactions/get", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_get_transaction(id_by_customer: str) -> str:
    """Get a single transaction by its customer ID."""
    try:
        return _ok(_api_post("transactions/get/id_by_customer", {
            "id_by_customer": id_by_customer
        }))
    except Exception as e:
        return _err(e)


@mcp.tool()
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
    try:
        payload: dict = {
            "value_date": value_date,
            "account_number": account_number,
            "currency": currency,
        }
        if bank_code:
            payload["bank_code"] = bank_code
        if bank_name:
            payload["bank_name"] = bank_name
        if purpose:
            payload["purpose"] = purpose
        if type:
            payload["type"] = type
        if booking_text:
            payload["booking_text"] = booking_text
        if payment_reference:
            payload["payment_reference"] = payment_reference
        return _ok(_api_post("transactions/add", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_add_transactions_batch(transactions: list) -> str:
    """Add multiple transactions in batch. Each dict uses the same keys as bb_add_transaction."""
    try:
        return _ok(_api_post("transactions/addBatch", {"transactions": transactions}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_assign_receipt_to_transaction(
    receipt_id_by_customer: str,
    transaction_id_by_customer: str,
) -> str:
    """Assign a receipt to a transaction."""
    try:
        return _ok(_api_post("transactions/assign/receipt", {
            "receipt_id_by_customer": receipt_id_by_customer,
            "transaction_id_by_customer": transaction_id_by_customer,
        }))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_assign_receipts_to_transactions_batch(assignments: list) -> str:
    """Assign multiple receipts to transactions in batch. Each dict has: receipt_id_by_customer, transaction_id_by_customer."""
    try:
        return _ok(_api_post("transactions/assign-batch/receipt", {"assignments": assignments}))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_get_assigned_receipts(
    transaction_id_by_customer: str,
    confirmed_only: bool = False,
) -> str:
    """Get receipts assigned to a transaction."""
    try:
        payload: dict = {"transaction_id_by_customer": transaction_id_by_customer}
        if confirmed_only:
            payload["confirmed_only"] = True
        return _ok(_api_post("transactions/assigned-receipts/get", payload))
    except Exception as e:
        return _err(e)


@mcp.tool()
async def bb_unassign_receipt_from_transaction(
    receipt_id_by_customer: str,
    transaction_id_by_customer: str,
) -> str:
    """Unassign a receipt from a transaction."""
    try:
        return _ok(_api_post("transactions/unassign/receipt", {
            "receipt_id_by_customer": receipt_id_by_customer,
            "transaction_id_by_customer": transaction_id_by_customer,
        }))
    except Exception as e:
        return _err(e)


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
