import pytest
import json
from unittest.mock import patch
from server import bb_list_postings

@pytest.mark.asyncio
async def test_bb_list_postings_error():
    """Test that bb_list_postings handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_list_postings()
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_list_postings_success():
    """Test that bb_list_postings formats the payload and calls _api_post correctly"""
    mock_response = {"success": True, "postings": [{"id": "123"}]}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_list_postings(
            date_from="2024-01-01",
            date_to="2024-12-31",
            limit=100,
            offset=10,
            account="1000",
            postingaccount="1200",
            posting_status="open",
            cost_location="department-a",
            date_last_action_from="2024-01-01",
            date_last_action_to="2024-01-31",
            order="date ASC"
        )

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "postings/get",
            {
                "limit": 100,
                "offset": 10,
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
                "account": "1000",
                "postingaccount": "1200",
                "posting_status": "open",
                "cost_location": "department-a",
                "date_last_action_from": "2024-01-01",
                "date_last_action_to": "2024-01-31",
                "order": "date ASC"
            }
        )

        # Verify the response is correctly formatted JSON
        assert json.loads(result) == mock_response
