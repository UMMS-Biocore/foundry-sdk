import pytest
from unittest.mock import Mock, patch
from copy import deepcopy
from viafoundry.metadata import Metadata
from viafoundry.models.domain.metadata import (
    ProjectCreate,
    ProjectUpdate,
    CollectionCreate,
    CollectionUpdate,
    FieldCreate,
    FieldUpdate,
    DataEntryUpdate,
    SearchParams,
    FileAddRequest,
    VmetaFieldType,
)


class TestMetadata:
    """Test suite for Metadata class."""

    @pytest.fixture
    def mock_client(self):
        """Fixture for mocked client."""
        return Mock()

    @pytest.fixture
    def metadata(self, mock_client):
        """Fixture for Metadata instance."""
        return Metadata(mock_client)

    # --- Initialization Tests ---

    def test_initialization(self, metadata, mock_client):
        """Test Metadata initialization."""
        assert metadata.client == mock_client

    # --- Project Methods Tests ---

    def test_search_projects_with_dict(self, metadata, mock_client):
        """Test searching projects with dict search params."""
        mock_response = {"data": [{"name": "project1"}]}
        mock_client.call.return_value = mock_response

        search_params = {"filter": {"name": "test"}}
        result = metadata.search_projects(search_params)

        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/project/search", data=search_params
        )
        assert result == mock_response

    def test_search_projects_with_search_params_model(self, metadata, mock_client):
        """Test searching projects with SearchParams model."""
        mock_response = {"data": [{"name": "project1"}]}
        mock_client.call.return_value = mock_response

        search_params = SearchParams(take=10, skip=0)
        result = metadata.search_projects(search_params)

        expected_data = search_params.model_dump(exclude_none=True)
        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/project/search", data=expected_data
        )
        assert result == mock_response

    def test_search_projects_with_none(self, metadata, mock_client):
        """Test searching projects with no search params."""
        mock_response = {"data": []}
        mock_client.call.return_value = mock_response

        result = metadata.search_projects()

        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/project/search", data={}
        )
        assert result == mock_response

    def test_search_projects_error(self, metadata, mock_client):
        """Test error handling in search_projects."""
        mock_client.call.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            metadata.search_projects()

        assert "Error 2001: Failed to search projects: API Error" in str(
            exc_info.value)

    def test_create_project_with_dict(self, metadata, mock_client):
        """Test creating project with dict data."""
        mock_response = {"_id": "project123", "name": "Test Project"}
        mock_client.call.return_value = mock_response

        project_data = {"name": "Test Project", "label": "Test Label"}
        result = metadata.create_project(project_data)

        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/project/create", data=project_data
        )
        assert result == mock_response

    def test_create_project_with_model(self, metadata, mock_client):
        """Test creating project with ProjectCreate model."""
        mock_response = {"_id": "project123", "name": "Test Project"}
        mock_client.call.return_value = mock_response

        project_data = ProjectCreate(name="Test Project", label="Test Label")
        result = metadata.create_project(project_data)

        expected_data = project_data.model_dump(exclude_none=True)
        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/project/create", data=expected_data
        )
        assert result == mock_response

    def test_create_project_error(self, metadata, mock_client):
        """Test error handling in create_project."""
        mock_client.call.side_effect = Exception("Creation failed")

        project_data = {"name": "Test Project", "label": "Test Label"}

        with pytest.raises(Exception) as exc_info:
            metadata.create_project(project_data)

        assert "Error 2002: Failed to create project: Creation failed" in str(
            exc_info.value)

    def test_get_project_success(self, metadata, mock_client):
        """Test getting project by ID."""
        project_id = "project123"
        mock_response = {"_id": project_id, "name": "Test Project"}
        mock_client.call.return_value = mock_response

        result = metadata.get_project(project_id)

        mock_client.call.assert_called_once_with(
            "GET", f"/api/v1/vmeta/project/{project_id}"
        )
        assert result == mock_response

    def test_get_project_error(self, metadata, mock_client):
        """Test error handling in get_project."""
        project_id = "project123"
        mock_client.call.side_effect = Exception("Not found")

        with pytest.raises(Exception) as exc_info:
            metadata.get_project(project_id)

        assert f"Error 2003: Failed to get project {project_id}: Not found" in str(
            exc_info.value)

    def test_update_project_with_dict(self, metadata, mock_client):
        """Test updating project with dict data."""
        project_id = "project123"
        mock_response = {"_id": project_id, "name": "Updated Project"}
        mock_client.call.return_value = mock_response

        update_data = {"name": "Updated Project"}
        result = metadata.update_project(project_id, update_data)

        mock_client.call.assert_called_once_with(
            "PATCH", f"/api/v1/vmeta/project/{project_id}", data=update_data
        )
        assert result == mock_response

    def test_update_project_with_model(self, metadata, mock_client):
        """Test updating project with ProjectUpdate model."""
        project_id = "project123"
        mock_response = {"_id": project_id, "name": "Updated Project"}
        mock_client.call.return_value = mock_response

        update_data = ProjectUpdate(
            name="Updated Project", label="Updated Label")
        result = metadata.update_project(project_id, update_data)

        expected_data = update_data.model_dump(exclude_none=True)
        mock_client.call.assert_called_once_with(
            "PATCH", f"/api/v1/vmeta/project/{project_id}", data=expected_data
        )
        assert result == mock_response

    def test_update_project_error(self, metadata, mock_client):
        """Test error handling in update_project."""
        project_id = "project123"
        mock_client.call.side_effect = Exception("Update failed")

        update_data = {"name": "Updated Project"}

        with pytest.raises(Exception) as exc_info:
            metadata.update_project(project_id, update_data)

        assert f"Error 2004: Failed to update project {project_id}: Update failed" in str(
            exc_info.value)

    def test_delete_project_success(self, metadata, mock_client):
        """Test deleting project by ID."""
        project_id = "project123"
        mock_response = {"message": "Project deleted"}
        mock_client.call.return_value = mock_response

        result = metadata.delete_project(project_id)

        mock_client.call.assert_called_once_with(
            "DELETE", f"/api/v1/vmeta/project/{project_id}"
        )
        assert result == mock_response

    def test_delete_project_error(self, metadata, mock_client):
        """Test error handling in delete_project."""
        project_id = "project123"
        mock_client.call.side_effect = Exception("Deletion failed")

        with pytest.raises(Exception) as exc_info:
            metadata.delete_project(project_id)

        assert f"Error 2005: Failed to delete project {project_id}: Deletion failed" in str(
            exc_info.value)

    # --- Collection Methods Tests ---

    def test_search_collections_with_dict(self, metadata, mock_client):
        """Test searching collections with dict search params."""
        mock_response = {"data": [{"name": "collection1"}]}
        mock_client.call.return_value = mock_response

        search_params = {"filter": {"projectID": "project123"}}
        result = metadata.search_collections(search_params)

        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/collection/search", data=search_params
        )
        assert result == mock_response

    def test_search_collections_with_search_params_model(self, metadata, mock_client):
        """Test searching collections with SearchParams model."""
        mock_response = {"data": [{"name": "collection1"}]}
        mock_client.call.return_value = mock_response

        search_params = SearchParams(take=5)
        result = metadata.search_collections(search_params)

        expected_data = search_params.model_dump(exclude_none=True)
        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/collection/search", data=expected_data
        )
        assert result == mock_response

    def test_search_collections_with_none(self, metadata, mock_client):
        """Test searching collections with no search params."""
        mock_response = {"data": []}
        mock_client.call.return_value = mock_response

        result = metadata.search_collections()

        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/collection/search", data={}
        )
        assert result == mock_response

    def test_search_collections_error(self, metadata, mock_client):
        """Test error handling in search_collections."""
        mock_client.call.side_effect = Exception("Search failed")

        with pytest.raises(Exception) as exc_info:
            metadata.search_collections()

        assert "Error 2011: Failed to search collections: Search failed" in str(
            exc_info.value)

    def test_create_collection_with_dict(self, metadata, mock_client):
        """Test creating collection with dict data."""
        mock_response = {"_id": "collection123", "name": "Test Collection"}
        mock_client.call.return_value = mock_response

        collection_data = {
            "name": "Test Collection",
            "label": "Test Label",
            "projectID": "507f1f77bcf86cd799439011"
        }
        result = metadata.create_collection(collection_data)

        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/collection/create", data=collection_data
        )
        assert result == mock_response

    def test_create_collection_with_model(self, metadata, mock_client):
        """Test creating collection with CollectionCreate model."""
        mock_response = {"_id": "collection123", "name": "Test Collection"}
        mock_client.call.return_value = mock_response

        collection_data = CollectionCreate(
            name="Test Collection",
            label="Test Label",
            projectID="507f1f77bcf86cd799439011",
            dataDeleteProtected=True
        )
        result = metadata.create_collection(collection_data)

        expected_data = collection_data.model_dump(exclude_none=True)
        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/collection/create", data=expected_data
        )
        assert result == mock_response

    def test_create_collection_error(self, metadata, mock_client):
        """Test error handling in create_collection."""
        mock_client.call.side_effect = Exception("Creation failed")

        collection_data = {
            "name": "Test Collection",
            "label": "Test Label",
            "projectID": "507f1f77bcf86cd799439011"
        }

        with pytest.raises(Exception) as exc_info:
            metadata.create_collection(collection_data)

        assert "Error 2012: Failed to create collection: Creation failed" in str(
            exc_info.value)

    def test_get_collection_success(self, metadata, mock_client):
        """Test getting collection by ID."""
        collection_id = "collection123"
        mock_response = {"_id": collection_id, "name": "Test Collection"}
        mock_client.call.return_value = mock_response

        result = metadata.get_collection(collection_id)

        mock_client.call.assert_called_once_with(
            "GET", f"/api/v1/vmeta/collection/{collection_id}"
        )
        assert result == mock_response

    def test_get_collection_error(self, metadata, mock_client):
        """Test error handling in get_collection."""
        collection_id = "collection123"
        mock_client.call.side_effect = Exception("Not found")

        with pytest.raises(Exception) as exc_info:
            metadata.get_collection(collection_id)

        assert f"Error 2013: Failed to get collection {collection_id}: Not found" in str(
            exc_info.value)

    def test_update_collection_with_dict(self, metadata, mock_client):
        """Test updating collection with dict data."""
        collection_id = "collection123"
        mock_response = {"_id": collection_id, "name": "Updated Collection"}
        mock_client.call.return_value = mock_response

        update_data = {"name": "Updated Collection"}
        result = metadata.update_collection(collection_id, update_data)

        mock_client.call.assert_called_once_with(
            "PATCH", f"/api/v1/vmeta/collection/{collection_id}", data=update_data
        )
        assert result == mock_response

    def test_update_collection_with_model(self, metadata, mock_client):
        """Test updating collection with CollectionUpdate model."""
        collection_id = "collection123"
        mock_response = {"_id": collection_id, "name": "Updated Collection"}
        mock_client.call.return_value = mock_response

        update_data = CollectionUpdate(
            name="Updated Collection", label="Updated Label", projectID="507f1f77bcf86cd799439011", dataDeleteProtected=False)
        result = metadata.update_collection(collection_id, update_data)

        expected_data = update_data.model_dump(exclude_none=True)
        mock_client.call.assert_called_once_with(
            "PATCH", f"/api/v1/vmeta/collection/{collection_id}", data=expected_data
        )
        assert result == mock_response

    def test_update_collection_error(self, metadata, mock_client):
        """Test error handling in update_collection."""
        collection_id = "collection123"
        mock_client.call.side_effect = Exception("Update failed")

        update_data = {"name": "Updated Collection"}

        with pytest.raises(Exception) as exc_info:
            metadata.update_collection(collection_id, update_data)

        assert f"Error 2014: Failed to update collection {collection_id}: Update failed" in str(
            exc_info.value)

    def test_delete_collection_success(self, metadata, mock_client):
        """Test deleting collection by ID."""
        collection_id = "collection123"
        mock_response = {"message": "Collection deleted"}
        mock_client.call.return_value = mock_response

        result = metadata.delete_collection(collection_id)

        mock_client.call.assert_called_once_with(
            "DELETE", f"/api/v1/vmeta/collection/{collection_id}"
        )
        assert result == mock_response

    def test_delete_collection_error(self, metadata, mock_client):
        """Test error handling in delete_collection."""
        collection_id = "collection123"
        mock_client.call.side_effect = Exception("Deletion failed")

        with pytest.raises(Exception) as exc_info:
            metadata.delete_collection(collection_id)

        assert f"Error 2015: Failed to delete collection {collection_id}: Deletion failed" in str(
            exc_info.value)

    # --- Field Methods Tests ---

    def test_search_fields_with_dict(self, metadata, mock_client):
        """Test searching fields with dict search params."""
        mock_response = {"data": [{"name": "field1"}]}
        mock_client.call.return_value = mock_response

        search_params = {"filter": {"collectionID": "collection123"}}
        result = metadata.search_fields(search_params)

        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/field/search", data=search_params
        )
        assert result == mock_response

    def test_search_fields_with_search_params_model(self, metadata, mock_client):
        """Test searching fields with SearchParams model."""
        mock_response = {"data": [{"name": "field1"}]}
        mock_client.call.return_value = mock_response

        search_params = SearchParams(take=10)
        result = metadata.search_fields(search_params)

        expected_data = search_params.model_dump(exclude_none=True)
        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/field/search", data=expected_data
        )
        assert result == mock_response

    def test_search_fields_with_none(self, metadata, mock_client):
        """Test searching fields with no search params."""
        mock_response = {"data": []}
        mock_client.call.return_value = mock_response

        result = metadata.search_fields()

        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/field/search", data={}
        )
        assert result == mock_response

    def test_search_fields_error(self, metadata, mock_client):
        """Test error handling in search_fields."""
        mock_client.call.side_effect = Exception("Search failed")

        with pytest.raises(Exception) as exc_info:
            metadata.search_fields()

        assert "Error 2021: Failed to search fields: Search failed" in str(
            exc_info.value)

    def test_create_field_with_dict(self, metadata, mock_client):
        """Test creating field with dict data."""
        mock_response = {"_id": "field123", "name": "Test Field"}
        mock_client.call.return_value = mock_response

        field_data = {
            "name": "Test Field",
            "label": "Test Label",
            "type": "String",
            "collectionID": "507f1f77bcf86cd799439011"
        }
        result = metadata.create_field(field_data)

        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/field/create", data=field_data
        )
        assert result == mock_response

    def test_create_field_with_model(self, metadata, mock_client):
        """Test creating field with FieldCreate model."""
        mock_response = {"_id": "field123", "name": "Test Field"}
        mock_client.call.return_value = mock_response

        field_data = FieldCreate(
            name="Test Field",
            label="Test Label",
            type=VmetaFieldType.STRING,
            collectionID="507f1f77bcf86cd799439011",
            required=True
        )
        result = metadata.create_field(field_data)

        expected_data = field_data.model_dump(exclude_none=True)
        mock_client.call.assert_called_once_with(
            "POST", "/api/v1/vmeta/field/create", data=expected_data
        )
        assert result == mock_response

    def test_create_field_error(self, metadata, mock_client):
        """Test error handling in create_field."""
        mock_client.call.side_effect = Exception("Creation failed")

        field_data = {
            "name": "Test Field",
            "label": "Test Label",
            "type": "String",
            "collectionID": "507f1f77bcf86cd799439011"
        }

        with pytest.raises(Exception) as exc_info:
            metadata.create_field(field_data)

        assert "Error 2022: Failed to create field: Creation failed" in str(
            exc_info.value)

    def test_get_field_success(self, metadata, mock_client):
        """Test getting field by ID."""
        field_id = "field123"
        mock_response = {"_id": field_id, "name": "Test Field"}
        mock_client.call.return_value = mock_response

        result = metadata.get_field(field_id)

        mock_client.call.assert_called_once_with(
            "GET", f"/api/v1/vmeta/field/{field_id}"
        )
        assert result == mock_response

    def test_get_field_error(self, metadata, mock_client):
        """Test error handling in get_field."""
        field_id = "field123"
        mock_client.call.side_effect = Exception("Not found")

        with pytest.raises(Exception) as exc_info:
            metadata.get_field(field_id)

        assert f"Error 2023: Failed to get field {field_id}: Not found" in str(
            exc_info.value)

    def test_update_field_with_dict(self, metadata, mock_client):
        """Test updating field with dict data."""
        field_id = "field123"
        mock_response = {"_id": field_id, "name": "Updated Field"}
        mock_client.call.return_value = mock_response

        update_data = {"name": "Updated Field"}
        result = metadata.update_field(field_id, update_data)

        mock_client.call.assert_called_once_with(
            "PATCH", f"/api/v1/vmeta/field/{field_id}", data=update_data
        )
        assert result == mock_response

    def test_update_field_with_model(self, metadata, mock_client):
        """Test updating field with FieldUpdate model."""
        field_id = "field123"
        mock_response = {"_id": field_id, "name": "Updated Field"}
        mock_client.call.return_value = mock_response

        update_data = FieldUpdate(
            name="Updated Field",
            label="Updated Label",
            type=VmetaFieldType.NUMBER
        )
        result = metadata.update_field(field_id, update_data)

        expected_data = update_data.model_dump(exclude_none=True)
        mock_client.call.assert_called_once_with(
            "PATCH", f"/api/v1/vmeta/field/{field_id}", data=expected_data
        )
        assert result == mock_response

    def test_update_field_error(self, metadata, mock_client):
        """Test error handling in update_field."""
        field_id = "field123"
        mock_client.call.side_effect = Exception("Update failed")

        update_data = {"name": "Updated Field"}

        with pytest.raises(Exception) as exc_info:
            metadata.update_field(field_id, update_data)

        assert f"Error 2024: Failed to update field {field_id}: Update failed" in str(
            exc_info.value)

    def test_delete_field_success(self, metadata, mock_client):
        """Test deleting field by ID."""
        field_id = "field123"
        mock_response = {"message": "Field deleted"}
        mock_client.call.return_value = mock_response

        result = metadata.delete_field(field_id)

        mock_client.call.assert_called_once_with(
            "DELETE", f"/api/v1/vmeta/field/{field_id}"
        )
        assert result == mock_response

    def test_delete_field_error(self, metadata, mock_client):
        """Test error handling in delete_field."""
        field_id = "field123"
        mock_client.call.side_effect = Exception("Deletion failed")

        with pytest.raises(Exception) as exc_info:
            metadata.delete_field(field_id)

        assert f"Error 2025: Failed to delete field {field_id}: Deletion failed" in str(
            exc_info.value)

    def test_get_collection_fields_success(self, metadata, mock_client):
        """Test getting fields by collection ID."""
        collection_id = "collection123"
        mock_response = {"data": [{"name": "field1"}, {"name": "field2"}]}

        # Mock the search_fields method
        with patch.object(metadata, 'search_fields', return_value=mock_response) as mock_search:
            result = metadata.get_collection_fields(collection_id)

        # Verify search_fields was called with correct parameters
        expected_search_params = {
            "filter": {
                "collectionID": collection_id
            }
        }
        mock_search.assert_called_once_with(expected_search_params)
        assert result == mock_response

    def test_get_collection_fields_error(self, metadata, mock_client):
        """Test error handling in get_collection_fields."""
        collection_id = "collection123"

        # Mock search_fields to raise an exception
        with patch.object(metadata, 'search_fields', side_effect=Exception("Search failed")):
            with pytest.raises(Exception) as exc_info:
                metadata.get_collection_fields(collection_id)

        assert f"Error 2026: Failed to get fields for collection: {collection_id}: Search failed" in str(
            exc_info.value)

    def test_get_project_fields_success(self, metadata, mock_client):
        """Test getting all fields for a project."""
        project_id = "project123"

        # Mock search_collections response
        collections_response = {
            "data": [
                {"_id": "collection1", "name": "Collection 1"},
                {"_id": "collection2", "name": "Collection 2"}
            ]
        }

        # Mock get_collection_fields responses
        fields_response_1 = {"data": [{"name": "field1"}, {"name": "field2"}]}
        fields_response_2 = {"data": [{"name": "field3"}]}

        with patch.object(metadata, 'search_collections', return_value=collections_response) as mock_search_collections:
            with patch.object(metadata, 'get_collection_fields', side_effect=[fields_response_1, fields_response_2]) as mock_get_fields:
                result = metadata.get_project_fields(project_id)

        # Verify search_collections was called with correct parameters
        expected_search_params = {
            "filter": {
                "projectID": project_id
            }
        }
        mock_search_collections.assert_called_once_with(expected_search_params)

        # Verify get_collection_fields was called for each collection
        assert mock_get_fields.call_count == 2
        mock_get_fields.assert_any_call("collection1")
        mock_get_fields.assert_any_call("collection2")

        # Verify all fields are accumulated
        assert result == {"data": [{"name": "field1"}, {
            "name": "field2"}, {"name": "field3"}]}

    def test_get_project_fields_empty_collections(self, metadata, mock_client):
        """Test getting fields for project with no collections."""
        project_id = "project123"

        collections_response = {"data": []}

        with patch.object(metadata, 'search_collections', return_value=collections_response):
            result = metadata.get_project_fields(project_id)

        assert result == {"data": []}

    def test_get_project_fields_error(self, metadata, mock_client):
        """Test error handling in get_project_fields."""
        project_id = "project123"

        with patch.object(metadata, 'search_collections', side_effect=Exception("Search failed")):
            with pytest.raises(Exception) as exc_info:
                metadata.get_project_fields(project_id)

        assert f"Error 2027: Failed to get fields for project {project_id}: Search failed" in str(
            exc_info.value)

    # --- Dataset Methods Tests ---

    def test_search_dataset_files_success(self, metadata, mock_client):
        """Test searching dataset files."""
        dataset_id = "dataset123"
        filter_data = {"name": "*.csv"}
        mock_response = {"data": [{"name": "file1.csv"}]}
        mock_client.call.return_value = mock_response

        result = metadata.search_dataset_files(dataset_id, filter_data)

        mock_client.call.assert_called_once_with(
            "POST", f"/api/v1/vmeta/dataset/{dataset_id}/files/search", data=filter_data
        )
        assert result == mock_response

    def test_search_dataset_files_no_filter(self, metadata, mock_client):
        """Test searching dataset files without filter."""
        dataset_id = "dataset123"
        mock_response = {"data": []}
        mock_client.call.return_value = mock_response

        result = metadata.search_dataset_files(dataset_id)

        mock_client.call.assert_called_once_with(
            "POST", f"/api/v1/vmeta/dataset/{dataset_id}/files/search", data={}
        )
        assert result == mock_response

    def test_search_dataset_files_error(self, metadata, mock_client):
        """Test error handling in search_dataset_files."""
        dataset_id = "dataset123"
        mock_client.call.side_effect = Exception("Search failed")

        with pytest.raises(Exception) as exc_info:
            metadata.search_dataset_files(dataset_id)

        assert f"Error 2036: Failed to search dataset files for {dataset_id}: Search failed" in str(
            exc_info.value)

    def test_add_files_to_dataset_with_dict(self, metadata, mock_client):
        """Test adding files to dataset with dict data."""
        dataset_id = "dataset123"
        file_data = {
            "projectId": "66269972dc000cff1c8a54b0",
            "file": {"name": "test.csv", "path": "/data/test.csv"}
        }
        mock_response = {"message": "Files added"}
        mock_client.call.return_value = mock_response

        result = metadata.add_files_to_dataset(dataset_id, file_data)

        mock_client.call.assert_called_once_with(
            "POST", f"/api/v1/vmeta/dataset/{dataset_id}/addFile", data=file_data
        )
        assert result == mock_response

    def test_add_files_to_dataset_with_model(self, metadata, mock_client):
        """Test adding files to dataset with FileAddRequest model."""
        dataset_id = "dataset123"
        file_data = FileAddRequest(
            projectId="66269972dc000cff1c8a54b0",
            file={"name": "test.csv", "path": "/data/test.csv"}
        )
        mock_response = {"message": "Files added"}
        mock_client.call.return_value = mock_response

        result = metadata.add_files_to_dataset(dataset_id, file_data)

        expected_data = file_data.model_dump(exclude_none=True)
        mock_client.call.assert_called_once_with(
            "POST", f"/api/v1/vmeta/dataset/{dataset_id}/addFile", data=expected_data
        )
        assert result == mock_response

    def test_add_files_to_dataset_error(self, metadata, mock_client):
        """Test error handling in add_files_to_dataset."""
        dataset_id = "dataset123"
        file_data = {"projectId": "test", "file": {}}
        mock_client.call.side_effect = Exception("Add failed")

        with pytest.raises(Exception) as exc_info:
            metadata.add_files_to_dataset(dataset_id, file_data)

        assert f"Error 2037: Failed to add files to dataset {dataset_id}: Add failed" in str(
            exc_info.value)

    # --- Data Methods Tests ---

    def test_search_data_success(self, metadata, mock_client):
        """Test searching data entries."""
        project_id = "project123"
        collection_name = "samples"
        filter_data = {"status": "active"}
        mock_response = {"data": [{"_id": "data1", "name": "Sample 1"}]}
        mock_client.call.return_value = mock_response

        result = metadata.search_data(project_id, collection_name, filter_data)

        mock_client.call.assert_called_once_with(
            "POST", f"/api/v1/vmeta/project/{project_id}/data/{collection_name}/search", data=filter_data
        )
        assert result == mock_response

    def test_search_data_no_filter(self, metadata, mock_client):
        """Test searching data entries without filter."""
        project_id = "project123"
        collection_name = "samples"
        mock_response = {"data": []}
        mock_client.call.return_value = mock_response

        result = metadata.search_data(project_id, collection_name)

        mock_client.call.assert_called_once_with(
            "POST", f"/api/v1/vmeta/project/{project_id}/data/{collection_name}/search", data={}
        )
        assert result == mock_response

    def test_search_data_error(self, metadata, mock_client):
        """Test error handling in search_data."""
        project_id = "project123"
        collection_name = "samples"
        mock_client.call.side_effect = Exception("Search failed")

        with pytest.raises(Exception) as exc_info:
            metadata.search_data(project_id, collection_name)

        assert f"Error 2041: Failed to search data for {collection_name}: Search failed" in str(
            exc_info.value)

    def test_get_data_success(self, metadata, mock_client):
        """Test getting data entry by ID."""
        project_id = "project123"
        collection_name = "samples"
        data_id = "data123"
        mock_response = {"_id": data_id, "name": "Sample 1"}
        mock_client.call.return_value = mock_response

        result = metadata.get_data(project_id, collection_name, data_id)

        mock_client.call.assert_called_once_with(
            "GET", f"/api/v1/vmeta/project/{project_id}/data/{collection_name}/{data_id}"
        )
        assert result == mock_response

    def test_get_data_error(self, metadata, mock_client):
        """Test error handling in get_data."""
        project_id = "project123"
        collection_name = "samples"
        data_id = "data123"
        mock_client.call.side_effect = Exception("Not found")

        with pytest.raises(Exception) as exc_info:
            metadata.get_data(project_id, collection_name, data_id)

        assert f"Error 2042: Failed to get data {data_id}: Not found" in str(
            exc_info.value)

    def test_update_data_with_dict(self, metadata, mock_client):
        """Test updating data entry with dict data."""
        project_id = "project123"
        collection_name = "samples"
        data_id = "data123"
        update_data = {"name": "Updated Sample"}
        mock_response = {"_id": data_id, "name": "Updated Sample"}
        mock_client.call.return_value = mock_response

        result = metadata.update_data(
            project_id, collection_name, data_id, update_data)

        mock_client.call.assert_called_once_with(
            "PATCH", f"/api/v1/vmeta/project/{project_id}/data/{collection_name}/{data_id}", data=update_data
        )
        assert result == mock_response

    def test_update_data_with_model(self, metadata, mock_client):
        """Test updating data entry with DataEntryUpdate model."""
        project_id = "project123"
        collection_name = "samples"
        data_id = "data123"
        update_data = DataEntryUpdate()
        # Add some fields to the model
        update_data.__dict__["name"] = "Updated Sample"
        update_data.__dict__["status"] = "processed"

        mock_response = {"_id": data_id, "name": "Updated Sample"}
        mock_client.call.return_value = mock_response

        result = metadata.update_data(
            project_id, collection_name, data_id, update_data)

        expected_data = update_data.model_dump(exclude_none=True)
        mock_client.call.assert_called_once_with(
            "PATCH", f"/api/v1/vmeta/project/{project_id}/data/{collection_name}/{data_id}", data=expected_data
        )
        assert result == mock_response

    def test_update_data_error(self, metadata, mock_client):
        """Test error handling in update_data."""
        project_id = "project123"
        collection_name = "samples"
        data_id = "data123"
        update_data = {"name": "Updated Sample"}
        mock_client.call.side_effect = Exception("Update failed")

        with pytest.raises(Exception) as exc_info:
            metadata.update_data(
                project_id, collection_name, data_id, update_data)

        assert f"Error 2043: Failed to update data {data_id}: Update failed" in str(
            exc_info.value)

    def test_delete_data_success(self, metadata, mock_client):
        """Test deleting data entry by ID."""
        project_id = "project123"
        collection_name = "samples"
        data_id = "data123"
        mock_response = {"message": "Data deleted"}
        mock_client.call.return_value = mock_response

        result = metadata.delete_data(project_id, collection_name, data_id)

        mock_client.call.assert_called_once_with(
            "DELETE", f"/api/v1/vmeta/project/{project_id}/data/{collection_name}/{data_id}"
        )
        assert result == mock_response

    def test_delete_data_error(self, metadata, mock_client):
        """Test error handling in delete_data."""
        project_id = "project123"
        collection_name = "samples"
        data_id = "data123"
        mock_client.call.side_effect = Exception("Deletion failed")

        with pytest.raises(Exception) as exc_info:
            metadata.delete_data(project_id, collection_name, data_id)

        assert f"Error 2044: Failed to delete data {data_id}: Deletion failed" in str(
            exc_info.value)

    # --- Helper Methods Tests ---

    def test_transfer_ownership_basic(self, metadata):
        """Test basic ownership transfer functionality."""
        original_obj = {
            "_id": "obj123",
            "name": "Test Object",
            "owner": {"_id": "oldowner", "name": "Old Owner"},
            "lastUpdatedUser": "olduser",
            "perms": ["read", "write"],
            "restrictTo": ["group1"]
        }

        new_owner = {
            "owner": {"_id": "newowner", "name": "New Owner", "email": "new@example.com"}
        }

        result = metadata.transfer_ownership(original_obj, new_owner)

        # Verify ownership transfer
        assert result["owner"] == new_owner["owner"]
        assert result["lastUpdatedUser"] == "newowner"

        # Verify restricted fields are removed
        assert "perms" not in result
        assert "restrictTo" not in result

        # Verify other fields are preserved
        assert result["_id"] == "obj123"
        assert result["name"] == "Test Object"

        # Verify original object is not modified
        assert original_obj["owner"]["_id"] == "oldowner"

    def test_transfer_ownership_with_project_id(self, metadata):
        """Test ownership transfer with project ID update."""
        original_obj = {
            "_id": "obj123",
            "name": "Test Object",
            "projectID": "oldproject",
            "owner": {"_id": "oldowner", "name": "Old Owner"},
            "lastUpdatedUser": "olduser"
        }

        new_owner = {
            "owner": {"_id": "newowner", "name": "New Owner"}
        }

        result = metadata.transfer_ownership(
            original_obj, new_owner, project_id="newproject")

        # Verify project ID is updated
        assert result["projectID"] == "newproject"
        assert result["owner"] == new_owner["owner"]
        assert result["lastUpdatedUser"] == "newowner"

    def test_transfer_ownership_with_nested_objects(self, metadata):
        """Test ownership transfer with nested objects."""
        original_obj = {
            "_id": "obj123",
            "name": "Test Object",
            "owner": {"_id": "oldowner", "name": "Old Owner"},
            "children": [
                {
                    "owner": {"_id": "oldchildowner", "name": "Old Child Owner"},
                    "lastUpdatedUser": "oldchilduser",
                    "perms": ["read"]
                }
            ],
            "metadata": {
                "owner": {"_id": "oldmetaowner", "name": "Old Meta Owner"},
                "lastUpdatedUser": "oldmetauser"
            }
        }

        new_owner = {
            "owner": {"_id": "newowner", "name": "New Owner"}
        }

        result = metadata.transfer_ownership(original_obj, new_owner)

        # Verify nested ownership transfers
        assert result["owner"] == new_owner["owner"]
        assert result["children"][0]["owner"] == new_owner["owner"]
        assert result["children"][0]["lastUpdatedUser"] == "newowner"
        assert result["metadata"]["owner"] == new_owner["owner"]
        assert result["metadata"]["lastUpdatedUser"] == "newowner"

        # Verify nested restricted fields are removed
        assert "perms" not in result["children"][0]

    def test_transfer_ownership_preserves_non_owner_fields(self, metadata):
        """Test that transfer_ownership preserves all non-owner/permission fields."""
        original_obj = {
            "_id": "obj123",
            "name": "Test Object",
            "description": "Test Description",
            "tags": ["tag1", "tag2"],
            "settings": {"key": "value"},
            "owner": {"_id": "oldowner", "name": "Old Owner"},
            "lastUpdatedUser": "olduser",
            "customField": "custom value",
            "nested": {
                "property": "nested value",
                "owner": {"_id": "nestedoldowner"},
                "lastUpdatedUser": "nestedolduser"
            }
        }

        new_owner = {
            "owner": {"_id": "newowner", "name": "New Owner"}
        }

        result = metadata.transfer_ownership(original_obj, new_owner)

        # Verify all non-owner fields are preserved
        assert result["name"] == "Test Object"
        assert result["description"] == "Test Description"
        assert result["tags"] == ["tag1", "tag2"]
        assert result["settings"] == {"key": "value"}
        assert result["customField"] == "custom value"
        assert result["nested"]["property"] == "nested value"

        # Verify ownership fields are updated
        assert result["owner"] == new_owner["owner"]
        assert result["lastUpdatedUser"] == "newowner"
        assert result["nested"]["owner"] == new_owner["owner"]
        assert result["nested"]["lastUpdatedUser"] == "newowner"
