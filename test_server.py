import json
import pytest
from unittest.mock import patch
from server import bb_list_accounts

@pytest.mark.asyncio
@patch("server._api_post")
async def test_bb_list_accounts_success(mock_api_post):
    # Setup
    mock_response = {"status": "success", "data": [{"id": 1, "name": "Test Account"}]}
    mock_api_post.return_value = mock_response

    # Execute
    result = await bb_list_accounts()

    # Assert
    mock_api_post.assert_called_once_with("accounts/get", {})
    assert result == json.dumps(mock_response, indent=2, ensure_ascii=False)

@pytest.mark.asyncio
@patch("server._api_post")
async def test_bb_list_accounts_error(mock_api_post):
    # Setup
    error_message = "API Error"
    mock_api_post.side_effect = Exception(error_message)

    # Execute
    result = await bb_list_accounts()

    # Assert
    mock_api_post.assert_called_once_with("accounts/get", {})
    assert result == f"Error: {error_message}"
