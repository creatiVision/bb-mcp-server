import pytest
import json
from unittest.mock import patch
from server import bb_update_cost_location

@pytest.mark.asyncio
async def test_bb_update_cost_location_success():
    """Test that bb_update_cost_location formats the payload and calls _api_post correctly"""
    mock_response = {"success": True, "code": "DE-123"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_update_cost_location(code="DE-123", name="New Cost Location Name")

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "cost-locations/update",
            {"code": "DE-123", "name": "New Cost Location Name"}
        )

        # Verify the response is correctly formatted JSON
        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_update_cost_location_error():
    """Test that bb_update_cost_location handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_update_cost_location(code="DE-123", name="New Cost Location Name")
        assert result == "Error: API connection failed"
