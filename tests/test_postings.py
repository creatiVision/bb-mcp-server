import pytest
from unittest.mock import patch
from server import bb_create_postings_batch_free
import json

@pytest.mark.asyncio
async def test_bb_create_postings_batch_free_success():
    """Test that bb_create_postings_batch_free formats the payload and calls _api_post correctly"""
    mock_response = {"success": True, "ids": ["123", "124"]}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        free_postings = [
            {"account": "1000", "amount": 100.50, "postingaccount": "4000"},
            {"account": "1200", "amount": 200.00, "postingaccount": "4400", "date": "2023-10-01"}
        ]

        result = await bb_create_postings_batch_free(free_postings=free_postings)

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "postings/add-batch/free",
            {"free_postings": free_postings}
        )

        # Verify the response is correctly formatted JSON
        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_create_postings_batch_free_error():
    """Test that bb_create_postings_batch_free handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        free_postings = [
            {"account": "1000", "amount": 100.50, "postingaccount": "4000"}
        ]
        result = await bb_create_postings_batch_free(free_postings=free_postings)
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_create_postings_batch_free_empty():
    """Test that bb_create_postings_batch_free handles empty list correctly"""
    mock_response = {"success": True, "ids": []}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        free_postings = []
        result = await bb_create_postings_batch_free(free_postings=free_postings)
        mock_post.assert_called_once_with(
            "postings/add-batch/free",
            {"free_postings": free_postings}
        )
        assert json.loads(result) == mock_response
