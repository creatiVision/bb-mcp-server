import pytest
from unittest.mock import patch
from server import bb_create_einvoice
import json

@pytest.mark.asyncio
async def test_bb_create_einvoice_error():
    """Test that bb_create_einvoice handles API errors correctly"""
    with patch("server._api_post", side_effect=Exception("API connection failed")):
        result = await bb_create_einvoice(
            type="invoice",
            company_name="Test Company",
            item_name=["Item 1"],
            item_amount=[1],
            item_single_price=[100],
            item_tax_type=["S"],
            e_invoice_id="buyer_ref_123",
            street="Test Street 1",
            zip="12345",
            city="Test City",
            country="DE",
            email="test@example.com"
        )
        assert result == "Error: API connection failed"

@pytest.mark.asyncio
async def test_bb_create_einvoice_success_minimal():
    """Test bb_create_einvoice with minimal required arguments"""
    mock_response = {"success": True, "id": "einvoice_123"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_create_einvoice(
            type="invoice",
            company_name="Test Company",
            item_name=["Item 1"],
            item_amount=[1],
            item_single_price=[100],
            item_tax_type=["S"],
            e_invoice_id="buyer_ref_123",
            street="Test Street 1",
            zip="12345",
            city="Test City",
            country="DE",
            email="test@example.com"
        )

        mock_post.assert_called_once_with(
            "invoices/create/e-invoice",
            {
                "type": "invoice",
                "show_prices_type": "gross",
                "company_name": "Test Company",
                "date": "",
                "item_name": ["Item 1"],
                "item_amount": [1],
                "item_single_price": [100],
                "item_tax_type": ["S"],
                "e_invoice_id": "buyer_ref_123",
                "street": "Test Street 1",
                "zip": "12345",
                "city": "Test City",
                "country": "DE",
                "email": "test@example.com",
                "show_bankdata": False,
                "show_contactdata": False,
            }
        )

        assert json.loads(result) == mock_response

@pytest.mark.asyncio
async def test_bb_create_einvoice_success_optional():
    """Test bb_create_einvoice with optional arguments"""
    mock_response = {"success": True, "id": "einvoice_123"}
    with patch("server._api_post", return_value=mock_response) as mock_post:
        result = await bb_create_einvoice(
            type="invoice",
            company_name="Test Company",
            item_name=["Item 1", "Item 2"],
            item_amount=[1, 2],
            item_single_price=[100, 50],
            item_tax_type=["S", "S"],
            e_invoice_id="buyer_ref_123",
            street="Test Street 1",
            zip="12345",
            city="Test City",
            country="DE",
            email="test@example.com",
            item_tax_amount=[19, 19],
            item_unit=["Stk", "Stk"],
            item_description=["Desc 1", "Desc 2"],
            contact_person_name="Jane Doe",
            payment_reference="REF123"
        )

        mock_post.assert_called_once_with(
            "invoices/create/e-invoice",
            {
                "type": "invoice",
                "show_prices_type": "gross",
                "company_name": "Test Company",
                "date": "",
                "item_name": ["Item 1", "Item 2"],
                "item_amount": [1, 2],
                "item_single_price": [100, 50],
                "item_tax_type": ["S", "S"],
                "e_invoice_id": "buyer_ref_123",
                "street": "Test Street 1",
                "zip": "12345",
                "city": "Test City",
                "country": "DE",
                "email": "test@example.com",
                "show_bankdata": False,
                "show_contactdata": False,
                "item_tax_amount": [19, 19],
                "item_unit": ["Stk", "Stk"],
                "item_description": ["Desc 1", "Desc 2"],
                "contact_person_name": "Jane Doe",
                "payment_reference": "REF123",
            }
        )

        assert json.loads(result) == mock_response
