import pytest
from unittest.mock import patch
from server import bb_add_cost_location
import json

@pytest.mark.asyncio
async def test_bb_add_cost_location_error():
    """Test that bb_add_cost_location handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_add_cost_location(
            code="100",
            name="Marketing"
        )
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_add_cost_location_success():
    """Test that bb_add_cost_location formats the payload and calls _api_post correctly"""
    mock_response = {"success": True, "id": "456"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_add_cost_location(
            code="100",
            name="Marketing"
        )

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "cost-locations/add",
            {
                "code": "100",
                "name": "Marketing"
            }
        )

        # Verify the response is correctly formatted JSON
        assert json.loads(result) == mock_response
