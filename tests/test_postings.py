import pytest
import json
from unittest.mock import patch
from server import bb_create_postings_batch_transactions

@pytest.mark.asyncio
async def test_bb_create_postings_batch_transactions_error():
    """Test that bb_create_postings_batch_transactions handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_create_postings_batch_transactions(
            transaction_postings=[]
        )
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_create_postings_batch_transactions_success():
    """Test that bb_create_postings_batch_transactions formats the payload and calls _api_post correctly"""
    mock_response = {"success": True, "ids": ["123", "456"]}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        transaction_postings = [
            {
                "transaction_id_by_customer": "txn1",
                "postings": [{"account": "test", "amount": 100, "postingaccount": "1000"}]
            }
        ]
        result = await bb_create_postings_batch_transactions(
            transaction_postings=transaction_postings
        )

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "postings/add-batch/transactions",
            {"transaction_postings": transaction_postings}
        )

        # Verify the response is correctly formatted JSON
        assert json.loads(result) == mock_response
