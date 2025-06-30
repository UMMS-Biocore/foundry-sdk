import pytest
import pandas as pd
import os
from unittest.mock import Mock, patch, mock_open
from viafoundry.reports import Reports
from viafoundry.models.domain.reports import MultiReportData, FileUploadResponse, ReportPathsResponse
from tests.conftest import reports, sample_report_data, mock_client


class TestReports:
    """Test suite for Reports class."""

    def test_initialization(self, reports, mock_client):
        """Test Reports initialization."""
        assert reports.client == mock_client
        assert reports.enable_session_history is False

    def test_initialization_with_session_history(self, mock_client):
        """Test Reports initialization with session history enabled."""
        reports = Reports(mock_client, enable_session_history=True)
        assert reports.enable_session_history is True

    def test_get_process_names(self, reports, sample_report_data):
        """Test getting process names from report data."""
        processes = reports.get_process_names(sample_report_data)
        assert sorted(processes) == sorted(["process1", "process2"])

    def test_fetch_report_data(self, reports, mock_client):
        """Test fetching report data with file path injection."""
        mock_response = {
            "data": [{"processName": "process1", "routePath": "pubweb/path/to/file"}]
        }
        mock_client.call.return_value = mock_response

        result = reports.fetch_report_data("report123")

        # Verify API call
        mock_client.call.assert_called_once_with(
            "GET", "/api/run/v1/report123/reports/"
        )

        # Verify file_path injection
        assert result.data[0].file_path == "path/to/file"

    def test_fetch_report_data_error(self, reports, mock_client):
        """Test error handling in fetch_report_data."""
        mock_client.call.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            reports.fetch_report_data("report123")

        assert "Failed to fetch report data" in str(exc_info.value)
        assert "API Error" in str(exc_info.value)

    def test_get_process_names_with_pydantic_model(self, reports):
        """Test getting process names from MultiReportData model."""
        mock_data = MultiReportData(
            total=2,
            data=[
                {"processName": "process1", "routePath": "path1"},
                {"processName": "process2", "routePath": "path2"}
            ]
        )
        processes = reports.get_process_names(mock_data)
        assert sorted(processes) == sorted(["process1", "process2"])

    def test_get_process_names_empty_data(self, reports):
        """Test getting process names from empty data."""
        empty_data = {"data": []}
        processes = reports.get_process_names(empty_data)
        assert processes == []

    def test_get_file_names_success(self, reports):
        """Test getting file names for a specific process."""
        mock_data = {
            "data": [
                {
                    "processName": "process1",
                    "children": [
                        {
                            "id": "file1",
                            "name": "test.txt",
                            "extension": "txt",
                            "file_path": "path/to/test.txt",
                            "fileSize": 1024,
                            "routePath": "pubweb/path/to/test.txt",
                            "processName": "process1"
                        }
                    ]
                }
            ]
        }

        result = reports.get_file_names(mock_data, "process1")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["name"] == "test.txt"
        assert result.iloc[0]["extension"] == "txt"

    def test_get_file_names_with_nested_directories(self, reports):
        """Test getting file names with nested directory structure."""
        mock_data = {
            "data": [
                {
                    "processName": "process1",
                    "children": [
                        {
                            "id": "dir1",
                            "name": "subdir",
                            "extension": "dir",
                            "children": [
                                {
                                    "id": "file1",
                                    "name": "nested.csv",
                                    "extension": "csv",
                                    "file_path": "path/to/nested.csv",
                                    "fileSize": 2048,
                                    "routePath": "pubweb/path/to/nested.csv",
                                    "processName": "process1"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        result = reports.get_file_names(mock_data, "process1")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["name"] == "nested.csv"

    def test_get_file_names_process_not_found(self, reports):
        """Test getting file names for non-existent process."""
        mock_data = {"data": [{"processName": "process1", "children": []}]}

        with pytest.raises(RuntimeError) as exc_info:
            reports.get_file_names(mock_data, "nonexistent")

        assert "Process 'nonexistent' not found" in str(exc_info.value)

    def test_get_file_names_no_files(self, reports):
        """Test getting file names when no files exist."""
        mock_data = {
            "data": [{"processName": "process1", "children": []}]
        }

        with pytest.raises(RuntimeError) as exc_info:
            reports.get_file_names(mock_data, "process1")

        assert "No files found for process 'process1'" in str(exc_info.value)

    @patch('requests.get')
    def test_load_file_success_csv(self, mock_get, reports):
        """Test loading a CSV file successfully."""
        # Setup mock auth hostname
        reports.client.auth.hostname = "http://localhost"
        reports.client.auth.get_headers.return_value = {
            "Authorization": "Bearer test"}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "col1,col2\nvalue1,value2\nvalue3,value4"
        mock_get.return_value = mock_response

        mock_data = {
            "data": [
                {
                    "processName": "process1",
                    "children": [
                        {
                            "id": "file1",
                            "name": "test.csv",
                            "extension": "csv",
                            "file_path": "path/to/test.csv",
                            "fileSize": 1024,
                            "routePath": "/api/files/test.csv",
                            "processName": "process1"
                        }
                    ]
                }
            ]
        }

        result = reports.load_file(mock_data, "path/to/test.csv", sep=",")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ["col1", "col2"]

    @patch('requests.get')
    def test_load_file_success_text(self, mock_get, reports):
        """Test loading a text file successfully."""
        # Setup mock auth hostname
        reports.client.auth.hostname = "http://localhost"
        reports.client.auth.get_headers.return_value = {
            "Authorization": "Bearer test"}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "This is plain text content"
        mock_get.return_value = mock_response

        mock_data = {
            "data": [
                {
                    "processName": "process1",
                    "children": [
                        {
                            "id": "file1",
                            "name": "test.log",
                            "extension": "log",
                            "file_path": "path/to/test.log",
                            "fileSize": 1024,
                            "routePath": "/api/files/test.log",
                            "processName": "process1"
                        }
                    ]
                }
            ]
        }

        result = reports.load_file(mock_data, "path/to/test.log")

        assert result == "This is plain text content"

    def test_load_file_not_found(self, reports):
        """Test loading a file that doesn't exist."""
        mock_data = {
            "data": [
                {
                    "processName": "process1",
                    "children": [
                        {
                            "id": "file1",
                            "name": "existing.txt",
                            "extension": "txt",
                            "file_path": "path/to/existing.txt",
                            "fileSize": 1024,
                            "routePath": "/api/files/existing.txt",
                            "processName": "process1"
                        }
                    ]
                }
            ]
        }

        with pytest.raises(RuntimeError) as exc_info:
            reports.load_file(mock_data, "nonexistent.txt")

        assert "not found in the files of this report" in str(exc_info.value)

    @patch('requests.get')
    def test_load_file_http_error(self, mock_get, reports):
        """Test handling HTTP errors when loading files."""
        # Setup mock auth hostname
        reports.client.auth.hostname = "http://localhost"
        reports.client.auth.get_headers.return_value = {
            "Authorization": "Bearer test"}

        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        mock_data = {
            "data": [
                {
                    "processName": "process1",
                    "children": [
                        {
                            "id": "file1",
                            "name": "test.txt",
                            "extension": "txt",
                            "file_path": "path/to/test.txt",
                            "fileSize": 1024,
                            "routePath": "/api/files/test.txt",
                            "processName": "process1"
                        }
                    ]
                }
            ]
        }

        with pytest.raises(RuntimeError) as exc_info:
            reports.load_file(mock_data, "path/to/test.txt")

        assert "Failed to fetch file: HTTP 404" in str(exc_info.value)

    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_file_success(self, mock_file, mock_get, reports):
        """Test downloading a file successfully."""
        # Setup mock auth hostname
        reports.client.auth.hostname = "http://localhost"
        reports.client.auth.get_headers.return_value = {
            "Authorization": "Bearer test"}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"file content"
        mock_get.return_value = mock_response

        mock_data = {
            "data": [
                {
                    "processName": "process1",
                    "children": [
                        {
                            "id": "file1",
                            "name": "test.txt",
                            "extension": "txt",
                            "file_path": "path/to/test.txt",
                            "fileSize": 1024,
                            "routePath": "/api/files/test.txt",
                            "processName": "process1"
                        }
                    ]
                }
            ]
        }

        result = reports.download_file(mock_data, "path/to/test.txt", "/tmp")

        assert result == "/tmp/test.txt"
        mock_file.assert_called_once_with("/tmp/test.txt", "wb")

    def test_get_all_files_success(self, reports):
        """Test getting all files from report data."""
        mock_data = {
            "data": [
                {
                    "processName": "process1",
                    "children": [
                        {
                            "id": "file1",
                            "name": "test1.txt",
                            "extension": "txt",
                            "file_path": "path/to/test1.txt",
                            "fileSize": 1024,
                            "routePath": "/api/files/test1.txt"
                        }
                    ]
                },
                {
                    "processName": "process2",
                    "children": [
                        {
                            "id": "file2",
                            "name": "test2.csv",
                            "extension": "csv",
                            "file_path": "path/to/test2.csv",
                            "fileSize": 2048,
                            "routePath": "/api/files/test2.csv"
                        }
                    ]
                }
            ]
        }

        result = reports.get_all_files(mock_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "process1" in result["processName"].values
        assert "process2" in result["processName"].values

    def test_get_all_files_no_files(self, reports):
        """Test getting all files when no files exist."""
        mock_data = {"data": [{"processName": "process1", "children": []}]}

        with pytest.raises(RuntimeError) as exc_info:
            reports.get_all_files(mock_data)

        assert "No files found in the report" in str(exc_info.value)

    def test_get_all_report_paths_success(self, reports, mock_client):
        """Test getting all report paths successfully."""
        mock_response = {
            "data": [
                {"routePath": "/path1/pubweb/file1"},
                {"routePath": "/path2/pubweb/file2"},
                {"routePath": "/path1/pubweb/file3"}
            ]
        }
        mock_client.call.return_value = mock_response

        result = reports.get_all_report_paths("report123")

        assert isinstance(result, ReportPathsResponse)
        assert len(result.paths) == 3
        assert result.total_count == 3
        assert "/path1/pubweb/file1" in result.paths

    def test_get_all_report_paths_no_reports(self, reports, mock_client):
        """Test getting report paths when no reports exist."""
        mock_client.call.return_value = {"data": []}

        with pytest.raises(RuntimeError) as exc_info:
            reports.get_all_report_paths("report123")

        assert "No reports found" in str(exc_info.value)

    def test_get_report_dirs_success(self, reports, mock_client):
        """Test getting report directories successfully."""
        # Mock the get_all_report_paths method
        mock_response = ReportPathsResponse(
            paths=[
                "/report-resources/123/pubweb/dir1/file1",
                "/report-resources/123/pubweb/dir2/file2",
                "/report-resources/123/pubweb/dir1/file3"
            ],
            total_count=3
        )

        with patch.object(reports, 'get_all_report_paths', return_value=mock_response):
            result = reports.get_report_dirs("report123")

        assert "dir1/file1" in result
        assert "dir2/file2" in result

    @patch('builtins.open', new_callable=mock_open)
    @patch('mimetypes.guess_type')
    @patch('pathlib.Path.exists')
    def test_upload_report_file_success(self, mock_exists, mock_mime, mock_file, reports, mock_client):
        """Test uploading a file successfully."""
        mock_exists.return_value = True  # Mock file existence
        mock_mime.return_value = ("text/plain", None)

        # Mock get_all_report_paths
        mock_paths = ReportPathsResponse(
            paths=["/report-resources/123/pubweb/file1"],
            total_count=1
        )

        mock_client.call.return_value = {"file_id": "uploaded_file_123"}

        with patch.object(reports, 'get_all_report_paths', return_value=mock_paths):
            result = reports.upload_report_file(
                "report123", "/tmp/test.txt", "uploads")

        assert isinstance(result, FileUploadResponse)
        assert result.success is True
        assert "uploaded successfully" in result.message

    @patch('pathlib.Path.exists')
    def test_upload_report_file_file_not_exists(self, mock_exists, reports):
        """Test uploading a non-existent file."""
        mock_exists.return_value = False

        result = reports.upload_report_file(
            "report123", "/nonexistent/file.txt")

        assert isinstance(result, FileUploadResponse)
        assert result.success is False
        assert "File does not exist" in result.message

    @patch('viafoundry.reports.get_ipython')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.remove')
    def test_upload_session_history_success(self, mock_remove, mock_file, mock_ipython, reports):
        """Test uploading session history successfully."""
        # Mock IPython environment
        mock_ipython_instance = Mock()
        mock_ipython.return_value = mock_ipython_instance

        # Mock successful file upload
        mock_upload_response = FileUploadResponse(
            success=True,
            message="File uploaded successfully",
            file_id="history_123"
        )

        with patch.object(reports, 'upload_report_file', return_value=mock_upload_response):
            reports.enable_session_history = True
            result = reports.upload_session_history("report123", "history")

        # Verify the method completes without error
        assert mock_ipython.called

    def test_upload_session_history_disabled(self, reports):
        """Test uploading session history when disabled."""
        reports.enable_session_history = False

        with pytest.raises(Exception) as exc_info:
            reports.upload_session_history("report123")

        assert "Failed to upload session history" in str(exc_info.value)
        assert "Session history functionality is disabled" in str(
            exc_info.value)

    @patch('viafoundry.reports.get_ipython')
    def test_prepare_session_history_no_ipython(self, mock_ipython, reports):
        """Test preparing session history outside IPython environment."""
        mock_ipython.return_value = None

        with pytest.raises(Exception) as exc_info:
            reports.prepare_session_history()

        assert "IPython or Jupyter environments" in str(exc_info.value)

    def test_fetch_report_data_with_nested_children(self, reports, mock_client):
        """Test fetching report data with nested children structure."""
        mock_response = {
            "data": [
                {
                    "processName": "process1",
                    "routePath": "pubweb/parent/file",
                    "children": [
                        {
                            "processName": "child1",
                            "routePath": "pubweb/child/nested",
                            "children": []
                        }
                    ]
                }
            ]
        }
        mock_client.call.return_value = mock_response

        result = reports.fetch_report_data("report123")

        assert result.data[0].file_path == "parent/file"
        assert result.data[0].children[0].file_path == "child/nested"

    def test_fetch_report_data_no_pubweb_in_route(self, reports, mock_client):
        """Test fetching report data with routes that don't contain 'pubweb'."""
        mock_response = {
            "data": [
                {
                    "processName": "process1",
                    "routePath": "/some/other/path/file"
                }
            ]
        }
        mock_client.call.return_value = mock_response

        result = reports.fetch_report_data("report123")

        assert result.data[0].file_path is None

    def test_error_handling_methods(self, reports):
        """Test the _raise_error method."""
        with pytest.raises(RuntimeError) as exc_info:
            reports._raise_error(999, "Test error message")

        assert "Error 999: Test error message" in str(exc_info.value)
