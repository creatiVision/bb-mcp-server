import pytest
from unittest.mock import patch
from server import bb_unconfirm_transaction_posting

@pytest.mark.asyncio
async def test_bb_unconfirm_transaction_posting_error():
    """Test that bb_unconfirm_transaction_posting handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_unconfirm_transaction_posting(
            transaction_id_by_customer=12345
        )
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_unconfirm_transaction_posting_success():
    """Test that bb_unconfirm_transaction_posting formats the payload and calls _api_post correctly"""
    mock_response = {"success": True}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_unconfirm_transaction_posting(
            transaction_id_by_customer=12345
        )

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "postings/unconfirm/transaction",
            {
                "transaction_id_by_customer": 12345,
            }
        )

        # Verify the response is correctly formatted JSON
        import json
        assert json.loads(result) == mock_response
