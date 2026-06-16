import unittest
from unittest.mock import patch
import base64
import server

class TestAuthHeaders(unittest.TestCase):
    def test_auth_headers_both_missing(self):
        """Test _auth_headers when both API_CLIENT and API_SECRET are missing."""
        with patch('server.API_CLIENT', ''), patch('server.API_SECRET', ''):
            self.assertEqual(server._auth_headers(), {})

    def test_auth_headers_client_missing(self):
        """Test _auth_headers when API_CLIENT is missing but API_SECRET is present."""
        with patch('server.API_CLIENT', ''), patch('server.API_SECRET', 'secret_value'):
            self.assertEqual(server._auth_headers(), {})

    def test_auth_headers_secret_missing(self):
        """Test _auth_headers when API_CLIENT is present but API_SECRET is missing."""
        with patch('server.API_CLIENT', 'client_value'), patch('server.API_SECRET', ''):
            self.assertEqual(server._auth_headers(), {})

    def test_auth_headers_both_present(self):
        """Test _auth_headers when both API_CLIENT and API_SECRET are present."""
        client = "test_client"
        secret = "test_secret"
        with patch('server.API_CLIENT', client), patch('server.API_SECRET', secret):
            headers = server._auth_headers()
            expected_credentials = base64.b64encode(f"{client}:{secret}".encode()).decode()
            self.assertEqual(headers, {
                "Authorization": f"Basic {expected_credentials}",
                "Content-Type": "application/json",
            })

if __name__ == '__main__':
    unittest.main()
