#!/usr/bin/env python3
"""
BuchhaltungsButler MCP Server
Wraps the BuchhaltungsButler REST API for invoice/accounting automation.

API Docs: https://app.buchhaltungsbutler.de/docs/api/v1/
Swagger: https://app.buchhaltungsbutler.de/docs/api/v1.de.json
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
    """POST to BuchhaltungsButler API. All endpoints use POST."""
    url = f"{API_BASE_URL}/{endpoint}"
    # api_key goes in the JSON body per API spec
    payload = {**payload, "api_key": API_KEY}
    r = httpx.post(url, headers=_auth_headers(), json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


# ── RECEIPTS (BELEGE) ──

@mcp.tool()
async def bb_list_receipts(
    list_direction: str = "inbound",
    date_from: str = "",
    date_to: str = "",
    limit: int = 500,
    offset: int = 0,
    payment_status: str = "",
    counterparty: str = "",
) -> str:
    """List receipts (Belege). list_direction: 'inbound' (Eingang) or 'outbound' (Ausgang/Rechnungen)."""
    try:
        payload = {
            "list_direction": list_direction,
            "limit": limit,
            "offset": offset,
        }
        if date_from:
            payload["date_from"] = date_from
        if date_to:
            payload["date_to"] = date_to
        if payment_status:
            payload["payment_status"] = payment_status
        if counterparty:
            payload["counterparty"] = counterparty
        data = _api_post("receipts/get", payload)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
async def bb_get_receipt(receipt_id_by_customer: str) -> str:
    """Get a single receipt by its customer ID."""
    try:
        data = _api_post("receipts/get/id_by_customer", {
            "receipt_id_by_customer": receipt_id_by_customer
        })
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
async def bb_upload_receipt(
    filename: str,
    file_base64: str,
    list_direction: str = "inbound",
) -> str:
    """Upload a receipt (PDF/image). file_base64 must be base64-encoded file content."""
    try:
        data = _api_post("receipts/upload", {
            "filename": filename,
            "file": file_base64,
            "list_direction": list_direction,
        })
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


# ── INVOICES (RECHNUNGEN) ──

@mcp.tool()
async def bb_create_invoice(
    type: str,
    company_name: str,
    item_name: str,
    item_amount: float,
    item_single_price: float,
    item_vat: float = 19.0,
    date: str = "",
    street: str = "",
    zip: str = "",
    city: str = "",
    country: str = "DE",
    email: str = "",
    invoicenumber: str = "",
) -> str:
    """Create an invoice (Rechnung). type: ' outgoing_invoice' or 'credit_note'."""
    try:
        payload = {
            "type": type,
            "company_name": company_name,
            "item_name": item_name,
            "item_amount": item_amount,
            "item_single_price": item_single_price,
            "item_vat": item_vat,
            "show_prices_type": "gross",
        }
        if date:
            payload["date"] = date
        if street:
            payload["street"] = street
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
        data = _api_post("invoices/create", payload)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


# ── ACCOUNTS (KONTEN) ──

@mcp.tool()
async def bb_list_accounts() -> str:
    """List all accounts (Konten)."""
    try:
        data = _api_post("accounts/get", {})
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


# ── DEBTORS / CREDITORS (DEBITOREN / KREDITOREN) ──

@mcp.tool()
async def bb_list_debtors(limit: int = 500, offset: int = 0) -> str:
    """List all debtors (Debitoren / Kunden)."""
    try:
        data = _api_post("settings/get/debtors", {"limit": limit, "offset": offset})
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
async def bb_list_creditors(limit: int = 500, offset: int = 0) -> str:
    """List all creditors (Kreditoren / Lieferanten)."""
    try:
        data = _api_post("settings/get/creditors", {"limit": limit, "offset": offset})
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
async def bb_list_postingaccounts(limit: int = 500, offset: int = 0) -> str:
    """List all posting accounts (Buchungskonten)."""
    try:
        data = _api_post("settings/get/postingaccounts", {"limit": limit, "offset": offset})
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


# ── POSTINGS (BUCHUNGSSÄTZE) ──

@mcp.tool()
async def bb_list_postings(
    date_from: str = "2025-01-01",
    date_to: str = "",
    limit: int = 500,
    offset: int = 0,
    account: str = "",
    posting_status: str = "",
) -> str:
    """List all postings (Buchungssätze). Default date_from: 2025-01-01."""
    try:
        payload = {
            "limit": limit,
            "offset": offset,
            "date_from": date_from,
        }
        if date_to:
            payload["date_to"] = date_to
        if account:
            payload["account"] = account
        if posting_status:
            payload["posting_status"] = posting_status
        data = _api_post("postings/get", payload)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
async def bb_create_posting(
    receipt_id_by_customer: str = "",
    transaction_id_by_customer: str = "",
    posting_type: str = "receipt",
    account: str = "",
    amount: float = 0.0,
    postingaccount: str = "",
    cost_location: str = "",
    date: str = "",
) -> str:
    """Create a posting (Buchungssatz). posting_type: 'receipt', 'transaction', or 'free'."""
    try:
        if posting_type == "receipt" and receipt_id_by_customer:
            endpoint = "postings/add/receipt"
            payload = {
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
        data = _api_post(endpoint, payload)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


# ── COMMENTS ──

@mcp.tool()
async def bb_add_comment(
    comment_text: str,
    receipt_id_by_customer: str = "",
    transaction_id_by_customer: str = "",
) -> str:
    """Add a comment to a receipt or transaction."""
    try:
        payload = {"comment_text": comment_text}
        if receipt_id_by_customer:
            payload["receipt_id_by_customer"] = receipt_id_by_customer
        if transaction_id_by_customer:
            payload["transaction_id_by_customer"] = transaction_id_by_customer
        data = _api_post("comments/add", payload)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    import sys
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
