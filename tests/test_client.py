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

    def test_client_configure_auth(self, client, mock_auth, mocker):
        """Test client authentication configuration."""
        # Mock the POST request
        mock_post = mocker.patch("viafoundry.auth.requests.post")
        mock_post.return_value = Mock(
            status_code=200, json=lambda: {"token": "mock_token"}
        )

        # Configure auth
        client.configure_auth("http://localhost", "user", "pass")

        # Verify configuration
        mock_auth.configure.assert_called_once_with(
            "http://localhost", "user", "pass", "1", "http://localhost/user"
        )

    def test_discover(self, client, mock_auth, mocker):
        """Test API endpoint discovery functionality."""
        # Mock the GET request
        mock_get = mocker.patch("viafoundry.auth.requests.get")
        mock_get.return_value = Mock(
            status_code=200,
            headers={"Content-Type": "application/json"},
            json=lambda: {"paths": {"endpoint1": {}}},
        )

        endpoints = client.discover()

        # Verify endpoints and request
        assert "endpoint1" in endpoints
        mock_get.assert_called_once_with(
            "http://localhost/swagger.json",
            headers={"Authorization": "Bearer mock_token"},
        )

    def test_discover_error_handling(self, client, mock_auth, mocker):
        """Test error handling during API endpoint discovery."""
        # Mock failed GET request
        mock_get = mocker.patch("viafoundry.auth.requests.get")
        mock_response = Mock(
            status_code=404,
            headers={"Content-Type": "application/json"},
            json=lambda: {"error": "Not found"},
        )
        mock_response.raise_for_status = Mock(
            side_effect=requests.exceptions.HTTPError(response=mock_response)
        )
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            client.discover()

        assert "Failed to fetch endpoints" in str(exc_info.value)
