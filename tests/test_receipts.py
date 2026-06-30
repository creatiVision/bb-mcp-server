import pytest
from unittest.mock import patch
import json
from server import bb_upload_receipt

@pytest.mark.asyncio
async def test_bb_upload_receipt_error():
    """Test that bb_upload_receipt handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_upload_receipt(
            filename="receipt.pdf",
            file_base64="base64_encoded_content",
            list_direction="inbound",
        )
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_upload_receipt_success():
    """Test that bb_upload_receipt formats the payload and calls _api_post correctly"""
    mock_response = {"success": True, "id": "123"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_upload_receipt(
            filename="test_receipt.pdf",
            file_base64="SGVsbG8gV29ybGQ=",
            list_direction="inbound",
            account=1234,
            amount=100.50,
            currency="USD"
        )

        # Verify the API was called with the correct payload
        mock_post.assert_called_once_with(
            "receipts/upload",
            {
                "filename": "test_receipt.pdf",
                "file": "SGVsbG8gV29ybGQ=",
                "list_direction": "inbound",
                "account": 1234,
                "amount": 100.50,
                "currency": "USD"
            }
        )

        # Verify the response is correctly formatted JSON
        assert json.loads(result) == mock_response
