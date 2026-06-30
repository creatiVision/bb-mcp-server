import pytest
import json
from unittest.mock import patch
from server import bb_create_postings_batch_receipts

@pytest.mark.asyncio
async def test_bb_create_postings_batch_receipts_error():
    """Test that bb_create_postings_batch_receipts handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_create_postings_batch_receipts(
            [{"receipt_id_by_customer": "123", "postings": []}]
        )
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_create_postings_batch_receipts_success():
    """Test that bb_create_postings_batch_receipts formats the payload and calls _api_post correctly"""
    mock_response = {"success": True, "id": "batch_123"}
    test_postings = [
        {
            "receipt_id_by_customer": "123",
            "postings": [{"account": "1000", "amount": 10.0, "postingaccount": "1200"}],
            "cost_locations": ["loc1"],
            "cost_locations_two": ["loc2"]
        }
    ]

    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_create_postings_batch_receipts(test_postings)

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "postings/add-batch/receipts",
            {
                "receipt_postings": test_postings
            }
        )

        # Verify the response is correctly formatted JSON
        assert json.loads(result) == mock_response
