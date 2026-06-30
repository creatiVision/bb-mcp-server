import pytest
import json
from unittest.mock import patch
from server import bb_list_cost_locations

@pytest.mark.asyncio
async def test_bb_list_cost_locations_success_no_code():
    """Test bb_list_cost_locations handles success without code correctly"""
    mock_response = [{"id": "1", "code": "100", "name": "Marketing"}, {"id": "2", "code": "200", "name": "Sales"}]
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_list_cost_locations(limit=50, offset=10)

        mock_post.assert_called_once_with(
            "cost-locations/get",
            {
                "limit": 50,
                "offset": 10
            }
        )
        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_list_cost_locations_success_with_code():
    """Test bb_list_cost_locations handles success with code correctly"""
    mock_response = [{"id": "1", "code": "100", "name": "Marketing"}]
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_list_cost_locations(code="100", limit=1000, offset=0)

        mock_post.assert_called_once_with(
            "cost-locations/get",
            {
                "limit": 1000,
                "offset": 0,
                "code": "100"
            }
        )
        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_list_cost_locations_error():
    """Test bb_list_cost_locations handles errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_list_cost_locations(limit=10, offset=0)
        assert result == "Error: API connection failed"
