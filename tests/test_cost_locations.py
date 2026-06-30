import pytest
import json
from unittest.mock import patch
from server import bb_delete_cost_location

@pytest.mark.asyncio
async def test_bb_delete_cost_location_error():
    """Test that bb_delete_cost_location handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_delete_cost_location(code="TEST-CODE")
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_delete_cost_location_success():
    """Test that bb_delete_cost_location calls _api_post correctly"""
    mock_response = {"success": True}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_delete_cost_location(code="TEST-CODE")

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "cost-locations/delete",
            {"code": "TEST-CODE"}
        )

        # Verify the response is correctly formatted JSON
        assert json.loads(result) == mock_response
