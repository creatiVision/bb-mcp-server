import pytest
import json
from unittest.mock import patch
from server import bb_assign_receipt_to_free_posting

@pytest.mark.asyncio
async def test_bb_assign_receipt_to_free_posting_error():
    """Test that bb_assign_receipt_to_free_posting handles API errors correctly."""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_assign_receipt_to_free_posting(
            receipt_id_by_customer=123,
            posting_id_by_customer=456
        )
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_assign_receipt_to_free_posting_success():
    """Test that bb_assign_receipt_to_free_posting formats the payload and calls _api_post correctly."""
    mock_response = {"success": True, "message": "Assigned successfully"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_assign_receipt_to_free_posting(
            receipt_id_by_customer=123,
            posting_id_by_customer=456
        )

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "postings/assign/receipt-to-free-posting",
            {
                "receipt_id_by_customer": 123,
                "posting_id_by_customer": 456,
            }
        )

        # Verify the response is correctly formatted JSON
        assert json.loads(result) == mock_response
