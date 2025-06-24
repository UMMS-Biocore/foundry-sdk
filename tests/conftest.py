import pytest
from unittest.mock import Mock
from viafoundry.client import ViaFoundryClient
from viafoundry.reports import Reports


@pytest.fixture
def mock_auth(mocker):
    """Fixture for mocked Auth class."""
    mock = mocker.patch("viafoundry.auth.Auth")
    mock_instance = mock.return_value
    mock_instance.configure.return_value = None
    mock_instance.hostname = "http://localhost"
    mock_instance.get_headers.return_value = {
        "Authorization": "Bearer mock_token"}
    return mock_instance


@pytest.fixture
def client(mock_auth):
    """Fixture for ViaFoundryClient with mocked auth."""
    client = ViaFoundryClient()
    client.auth = mock_auth
    return client


@pytest.fixture
def mock_client():
    """Fixture for mocked client."""
    return Mock()


@pytest.fixture
def reports(mock_client):
    """Fixture for Reports instance."""
    return Reports(mock_client)


@pytest.fixture
def sample_report_data():
    """Fixture for sample report data."""
    return {
        "data": [
            {
                "processName": "process1",
                "routePath": "pubweb/path/to/process1",
                "children": [],
            },
            {
                "processName": "process2",
                "routePath": "path/to/process2",
                "children": [],
            },
        ]
    }
