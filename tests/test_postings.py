import pytest
import json
from unittest.mock import patch
from server import bb_create_posting

@pytest.mark.asyncio
async def test_bb_create_posting_error():
    """Test that bb_create_posting handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_create_posting(
            posting_type="free",
            account="1200",
            amount=100.50,
            postingaccount="8400"
        )
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_create_posting_free():
    """Test that bb_create_posting handles 'free' posting correctly"""
    mock_response = {"success": True, "id": "free123"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_create_posting(
            posting_type="free",
            account="1200",
            amount=100.50,
            postingaccount="8400",
            date="2023-10-27"
        )

        mock_post.assert_called_once_with(
            "postings/add/free",
            {
                "account": "1200",
                "amount": 100.50,
                "postingaccount": "8400",
                "date": "2023-10-27",
            }
        )
        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_create_posting_receipt():
    """Test that bb_create_posting handles 'receipt' posting correctly"""
    mock_response = {"success": True, "id": "rec123"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_create_posting(
            posting_type="receipt",
            account="1200",
            amount=100.50,
            postingaccount="8400",
            receipt_id_by_customer="cust_rec_001"
        )

        mock_post.assert_called_once_with(
            "postings/add/receipt",
            {
                "receipt_id_by_customer": "cust_rec_001",
                "postings": [{
                    "account": "1200",
                    "amount": 100.50,
                    "postingaccount": "8400",
                }],
            }
        )
        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_create_posting_transaction():
    """Test that bb_create_posting handles 'transaction' posting correctly"""
    mock_response = {"success": True, "id": "txn123"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_create_posting(
            posting_type="transaction",
            account="1200",
            amount=100.50,
            postingaccount="8400",
            transaction_id_by_customer="cust_txn_001"
        )

        mock_post.assert_called_once_with(
            "postings/add/transaction",
            {
                "transaction_id_by_customer": "cust_txn_001",
                "postings": [{
                    "account": "1200",
                    "amount": 100.50,
                    "postingaccount": "8400",
                }],
            }
        )
        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_create_posting_cost_locations():
    """Test that cost locations are added to the payload correctly"""
    mock_response = {"success": True, "id": "free123"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_create_posting(
            posting_type="free",
            account="1200",
            amount=100.50,
            postingaccount="8400",
            cost_location="Location1",
            cost_location_two="Location2"
        )

        mock_post.assert_called_once_with(
            "postings/add/free",
            {
                "account": "1200",
                "amount": 100.50,
                "postingaccount": "8400",
                "date": None,
                "cost_location": "Location1",
                "cost_location_two": "Location2",
            }
        )
        assert json.loads(result) == mock_response
