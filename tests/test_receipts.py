import pytest
from unittest.mock import patch
import json
from server import bb_list_receipts

@pytest.mark.asyncio
async def test_bb_list_receipts_error():
    """Test that bb_list_receipts handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_list_receipts()
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_list_receipts_success_default_params():
    """Test bb_list_receipts with default parameters"""
    mock_response = {"success": True, "receipts": []}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_list_receipts()

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "receipts/get",
            {
                "list_direction": "inbound",
                "limit": 500,
                "offset": 0,
                "include_offers": False,
                "deleted": False,
            }
        )

        # Verify the response is correctly formatted JSON
        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_list_receipts_success_all_params():
    """Test bb_list_receipts with all optional parameters"""
    mock_response = {"success": True, "receipts": [{"id": "1"}]}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_list_receipts(
            list_direction="outbound",
            date_from="2023-01-01",
            date_to="2023-12-31",
            limit=100,
            offset=50,
            payment_status="paid",
            counterparty="ACME Corp",
            include_offers=True,
            deleted=True,
            invoicenumber="INV-100",
            due_date="2023-12-01",
            order="date_desc",
        )

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "receipts/get",
            {
                "list_direction": "outbound",
                "limit": 100,
                "offset": 50,
                "include_offers": True,
                "deleted": True,
                "date_from": "2023-01-01",
                "date_to": "2023-12-31",
                "payment_status": "paid",
                "counterparty": "ACME Corp",
                "invoicenumber": "INV-100",
                "due_date": "2023-12-01",
                "order": "date_desc",
            }
        )

        # Verify the response is correctly formatted JSON
        assert json.loads(result) == mock_response
