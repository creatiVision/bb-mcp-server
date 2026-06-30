import pytest
import json
from unittest.mock import patch
from server import bb_get_receipt

@pytest.mark.asyncio
async def test_bb_get_receipt_success_without_file():
    """Test bb_get_receipt without requesting the file."""
    mock_response = {"success": True, "receipt": {"id": "123"}}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_get_receipt(receipt_id_by_customer="123")

        mock_post.assert_called_once_with(
            "receipts/get/id_by_customer",
            {"receipt_id_by_customer": "123"}
        )
        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_get_receipt_success_with_file():
    """Test bb_get_receipt requesting the file."""
    mock_response = {"success": True, "receipt": {"id": "123"}, "file": "base64_string"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_get_receipt(receipt_id_by_customer="123", get_file=True)

        mock_post.assert_called_once_with(
            "receipts/get/id_by_customer",
            {"receipt_id_by_customer": "123", "get_file": True}
        )
        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_get_receipt_error():
    """Test that bb_get_receipt handles API errors correctly."""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_get_receipt(receipt_id_by_customer="123")
        assert result == "Error: API connection failed"
