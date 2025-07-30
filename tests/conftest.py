import pytest
from unittest.mock import Mock
from viafoundry.client import ViaFoundryClient
from viafoundry.reports import Reports
from viafoundry.metadata import Metadata


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
def metadata(mock_client):
    """Fixture for Metadata instance."""
    return Metadata(mock_client)


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


@pytest.fixture
def sample_project_data():
    """Fixture for sample project data."""
    return {
        "_id": "507f1f77bcf86cd799439011",
        "name": "Test Project",
        "label": "Test Project Label",
        "description": "A test project",
        "owner": {
            "_id": "507f1f77bcf86cd799439012",
            "username": "testuser",
            "name": "Test User"
        }
    }


@pytest.fixture
def sample_collection_data():
    """Fixture for sample collection data."""
    return {
        "_id": "507f1f77bcf86cd799439013",
        "name": "Test Collection",
        "label": "Test Collection Label",
        "projectID": "507f1f77bcf86cd799439011",
        "description": "A test collection",
        "owner": {
            "_id": "507f1f77bcf86cd799439012",
            "username": "testuser",
            "name": "Test User"
        }
    }


@pytest.fixture
def sample_field_data():
    """Fixture for sample field data."""
    return {
        "_id": "507f1f77bcf86cd799439014",
        "name": "Test Field",
        "label": "Test Field Label",
        "type": "String",
        "collectionID": "507f1f77bcf86cd799439013",
        "required": True,
        "unique": False,
        "owner": {
            "_id": "507f1f77bcf86cd799439012",
            "username": "testuser",
            "name": "Test User"
        }
    }
