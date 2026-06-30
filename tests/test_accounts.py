import pytest
from unittest.mock import patch
from server import bb_add_account

@pytest.mark.asyncio
async def test_bb_add_account_error():
    """Test that bb_add_account handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_add_account(
            type="cash",
            name="Test Cash Account",
            postingaccount_number=1000
        )
        assert result == "Error: An unexpected error occurred."

@pytest.mark.asyncio
async def test_bb_add_account_success():
    """Test that bb_add_account formats the payload and calls _api_post correctly"""
    mock_response = {"success": True, "id": "123"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_add_account(
            type="cash",
            name="Test Cash Account",
            postingaccount_number=1000,
            receipt_creates_transaction=True,
            is_revision_safe=True
        )

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "accounts/add",
            {
                "type": "cash",
                "name": "Test Cash Account",
                "postingaccount_number": 1000,
                "receipt_creates_transaction": True,
                "is_revision_safe": True,
            }
        )

        # Verify the response is correctly formatted JSON
        import json
        assert json.loads(result) == mock_response
