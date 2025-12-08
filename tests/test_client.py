import pytest
import requests
from unittest.mock import Mock
from tests.conftest import client, mock_auth


class TestViaFoundryClient:
    """Test suite for ViaFoundryClient class."""

    def test_client_initialization(self, client, mock_auth):
        """Test that client initializes with proper components."""
        assert client.auth is mock_auth
        assert client.reports is not None

    def test_client_configure_auth(self, client, mock_auth):
        """Test client authentication configuration."""
        # Configure auth (mock_auth.configure is a Mock from fixture)
        client.configure_auth("http://localhost", "user", "pass")

        # Verify configuration
        mock_auth.configure.assert_called_once_with(
            "http://localhost", "user", "pass", None, 1, "http://localhost/user"
        )

    def test_discover(self, client, mock_auth, monkeypatch):
        """Test API endpoint discovery functionality."""
        calls = {}

        def fake_get(url, headers):
            calls["args"] = (url, headers)
            class Resp:
                status_code = 200
                headers = {"Content-Type": "application/json"}
                def raise_for_status(self):
                    return None
                def json(self):
                    return {"paths": {"endpoint1": {}}}
            return Resp()

        monkeypatch.setattr("viafoundry.client.requests.get", fake_get)

        endpoints = client.discover()

        # Verify endpoints and request
        assert "endpoint1" in endpoints
        assert calls["args"][0] == "http://localhost/swagger.json"
        assert calls["args"][1] == {"Authorization": "Bearer mock_token"}

    def test_discover_error_handling(self, client, mock_auth, monkeypatch):
        """Test error handling during API endpoint discovery."""
        # Mock failed GET request
        class Resp:
            status_code = 404
            headers = {"Content-Type": "application/json"}
            def raise_for_status(self):
                raise requests.exceptions.HTTPError(response=self)
            def json(self):
                return {"error": "Not found"}

        monkeypatch.setattr("viafoundry.client.requests.get", lambda url, headers: Resp())

        with pytest.raises(Exception) as exc_info:
            client.discover()

        assert "Failed to fetch endpoints" in str(exc_info.value)
