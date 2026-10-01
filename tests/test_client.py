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


class TestBadRequestMessage:
    """A 400 carries the server's reason, which tells the caller what to fix."""

    def _response(self, status, body=None, text=""):
        import requests
        response = requests.Response()
        response.status_code = status
        if body is not None:
            import json
            response._content = json.dumps(body).encode()
            response.headers["Content-Type"] = "application/json"
        else:
            response._content = text.encode()
        return response

    def test_400_passes_the_server_message_through(self, client):
        response = self._response(400, {"message": "names parameters that are not stored on process 5"})
        with pytest.raises(RuntimeError, match="not stored on process 5"):
            client._handle_http_error(response)

    def test_400_without_a_json_body_keeps_the_generic_message(self, client):
        response = self._response(400, text="<html>oops</html>")
        with pytest.raises(RuntimeError, match="Check the request parameters"):
            client._handle_http_error(response)

    def test_400_reads_an_error_key_too(self, client):
        response = self._response(400, {"error": "Forbidden field"})
        with pytest.raises(RuntimeError, match="Forbidden field"):
            client._handle_http_error(response)
