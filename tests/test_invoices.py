import pytest
import json
from unittest.mock import patch
from server import bb_create_invoice_draft

@pytest.mark.asyncio
async def test_bb_create_invoice_draft_success():
    """Test successful invoice draft creation."""
    mock_response = {"success": True, "id": "invoice-draft-123"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_create_invoice_draft(
            type="invoice",
            company_name="Test Company GmbH",
            item_name=["Consulting Services"],
            item_amount=[1],
            item_single_price=[1000.00],
            item_vat=[19],
            city="Berlin",
            country="DE",
            show_prices_type="net"
        )

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "invoices/create/draft",
            {
                "type": "invoice",
                "company_name": "Test Company GmbH",
                "item_name": ["Consulting Services"],
                "item_amount": [1],
                "item_single_price": [1000.00],
                "item_vat": [19],
                "city": "Berlin",
                "country": "DE",
                "show_prices_type": "net",
                "date": "",
                "show_bankdata": False,
                "show_contactdata": False
            }
        )

        # Verify result is correctly formatted JSON
        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_create_invoice_draft_error():
    """Test that bb_create_invoice_draft handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API timeout")):
        result = await bb_create_invoice_draft(
            type="invoice",
            company_name="Test Company",
            item_name=["Item"],
            item_amount=[1],
            item_single_price=[10.0],
            item_vat=[19]
        )
        assert result == "Error: API timeout"
