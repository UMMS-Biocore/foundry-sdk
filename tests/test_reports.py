import pytest
from viafoundry.reports import Reports
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
        assert result["data"][0]["file_path"] == "path/to/file"

    def test_fetch_report_data_error(self, reports, mock_client):
        """Test error handling in fetch_report_data."""
        mock_client.call.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            reports.fetch_report_data("report123")

        assert "Failed to fetch report data" in str(exc_info.value)
        assert "API Error" in str(exc_info.value)
