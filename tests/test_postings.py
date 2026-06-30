import pytest
from unittest.mock import patch
import json
from server import bb_unconfirm_free_posting

@pytest.mark.asyncio
async def test_bb_unconfirm_free_posting_error():
    """Test that bb_unconfirm_free_posting handles API errors correctly."""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_unconfirm_free_posting(posting_id_by_customer=12345)
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_unconfirm_free_posting_success():
    """Test that bb_unconfirm_free_posting calls API with correct parameters."""
    mock_response = {"success": True}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_unconfirm_free_posting(posting_id_by_customer=12345)

        # Verify API called with correct payload
        mock_post.assert_called_once_with(
            "postings/unconfirm/free",
            {"posting_id_by_customer": 12345}
        )

        # Verify JSON formatting of response
        assert json.loads(result) == mock_response
