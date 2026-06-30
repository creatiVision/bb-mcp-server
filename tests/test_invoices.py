import pytest
import json
from unittest.mock import patch
from server import bb_create_invoice

@pytest.mark.asyncio
async def test_bb_create_invoice_error():
    """Test that bb_create_invoice handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_create_invoice(
            type="invoice",
            company_name="Test Company",
            item_name=["Item 1"],
            item_amount=["1"],
            item_single_price=["100.00"],
            item_vat=["19"]
        )
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_create_invoice_success():
    """Test that bb_create_invoice formats the payload and calls _api_post correctly"""
    mock_response = {"success": True, "id": "12345"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_create_invoice(
            type="invoice",
            company_name="Test Company",
            item_name=["Item 1"],
            item_amount=["1"],
            item_single_price=["100.00"],
            item_vat=["19"],
            show_prices_type="net"
        )

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "invoices/create",
            {
                "type": "invoice",
                "show_prices_type": "net",
                "company_name": "Test Company",
                "date": "",
                "item_name": ["Item 1"],
                "item_amount": ["1"],
                "item_single_price": ["100.00"],
                "item_vat": ["19"],
                "show_bankdata": False,
                "show_contactdata": False,
                "country": "DE"
            }
        )

        # Verify the response is correctly formatted JSON
        assert json.loads(result) == mock_response
