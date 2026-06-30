import pytest
import json
from unittest.mock import patch
from server import bb_add_comment

@pytest.mark.asyncio
async def test_bb_add_comment_receipt_success():
    """Test that bb_add_comment formats the payload correctly for a receipt"""
    mock_response = {"success": True}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_add_comment(
            comment_text="Test comment for receipt",
            receipt_id_by_customer="receipt_123"
        )

        mock_post.assert_called_once_with(
            "comments/add",
            {
                "comment_text": "Test comment for receipt",
                "receipt_id_by_customer": "receipt_123"
            }
        )

        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_add_comment_transaction_success():
    """Test that bb_add_comment formats the payload correctly for a transaction"""
    mock_response = {"success": True}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_add_comment(
            comment_text="Test comment for transaction",
            transaction_id_by_customer="transaction_456"
        )

        mock_post.assert_called_once_with(
            "comments/add",
            {
                "comment_text": "Test comment for transaction",
                "transaction_id_by_customer": "transaction_456"
            }
        )

        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_add_comment_error():
    """Test that bb_add_comment handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_add_comment(
            comment_text="Test comment",
            receipt_id_by_customer="receipt_123"
        )
        assert result == "Error: API connection failed"
