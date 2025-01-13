import pytest
from unittest.mock import patch, Mock
from viafoundry.client import ViaFoundryClient


@patch('viafoundry.auth.Auth')
def test_client_initialization(mock_auth):
    # Mock the Auth class to ensure proper initialization
    mock_auth_instance = mock_auth.return_value
    mock_auth_instance.configure.return_value = None

    client = ViaFoundryClient()
    assert client.auth is not None  # Verify Auth is initialized
    assert client.reports is not None  # Verify Reports is initialized


@patch('viafoundry.auth.requests.post')  # Mock the POST request in Auth.login
@patch('viafoundry.auth.Auth')  # Mock the Auth class
def test_client_configure_auth(mock_auth, mock_post):
    # Mock the Auth class and its methods
    mock_auth_instance = mock_auth.return_value
    mock_auth_instance.configure.return_value = None

    # Debugging: Ensure the login method is invoked
    def mock_login(*args, **kwargs):
        print("Debug: Auth.login called")
        return "mock_token"
    mock_auth_instance.login.side_effect = mock_login

    # Mock the POST request
    def mock_post_request(url, *args, **kwargs):
        print(f"Debug: requests.post called with URL: {url} and args: {args}, kwargs: {kwargs}")
        return Mock(status_code=200, json=lambda: {"token": "mock_token"})
    mock_post.side_effect = mock_post_request

    # Initialize client and configure auth
    client = ViaFoundryClient()
    client.auth = mock_auth_instance
    client.configure_auth("http://localhost", "user", "pass")

    # Assertions
    mock_auth_instance.configure.assert_called_once_with(
        "http://localhost", "user", "pass", "1", "http://localhost/user"
    )


@patch('viafoundry.auth.requests.get')  # Mock the GET request in discover
@patch('viafoundry.auth.Auth')  # Mock the Auth class
def test_discover(mock_auth, mock_get):
    # Mock the Auth class
    mock_auth_instance = mock_auth.return_value
    mock_auth_instance.hostname = "http://localhost"
    mock_auth_instance.get_headers.return_value = {"Authorization": "Bearer mock_token"}

    # Mock API response for discover
    mock_get.return_value.status_code = 200
    mock_get.return_value.headers = {"Content-Type": "application/json"}
    mock_get.return_value.json.return_value = {"paths": {"endpoint1": {}}}

    # Pass the mocked Auth instance to ViaFoundryClient
    client = ViaFoundryClient()
    client.auth = mock_auth_instance
    endpoints = client.discover()

    assert "endpoint1" in endpoints

    # Ensure the GET request to the Swagger endpoint was made
    mock_get.assert_called_once_with(
        "http://localhost/swagger.json",
        headers={"Authorization": "Bearer mock_token"},
    )
