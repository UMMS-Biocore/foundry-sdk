import pytest
from unittest.mock import Mock
from viafoundry.reports import Reports


def test_get_process_names():
    reports = Reports(Mock())
    report_data = {"data": [{"processName": "process1"}, {"processName": "process2"}]}
    processes = reports.get_process_names(report_data)
    
    # Sort both lists to avoid order issues
    assert sorted(processes) == sorted(["process1", "process2"])


def test_some_other_functionality():
    # Example placeholder for additional tests for Reports
    reports = Reports(Mock())
    # Add your test logic here
    assert True
