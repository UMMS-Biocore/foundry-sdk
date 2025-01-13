import pytest
from unittest.mock import patch, Mock
from viafoundry.auth import Auth

@patch('viafoundry.auth.Auth.configure')
def test_auth_initialization(mock_configure):
    # Mock the configuration method
    mock_configure.return_value = None  # Simulate successful configuration
    auth = Auth(config_path="mock_path.json")
    assert auth  # Verify the Auth instance initializes successfully

@patch('viafoundry.auth.Auth.configure')
def test_auth_configure(mock_configure):
    # Test the configure method directly
    mock_configure.return_value = None  # Simulate successful configuration
    auth = Auth()
    auth.configure("https://hostname.com", "user", "pass")
    mock_configure.assert_called_once_with("https://hostname.com", "user", "pass")
