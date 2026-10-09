from unittest.mock import Mock

import pytest

from viafoundry.runs import Runs, default_execution_directory

ENV = {"id": 550, "username": "jdoe", "defWorkdir": None}


@pytest.fixture
def mock_client():
    return Mock()


@pytest.fixture
def runs(mock_client):
    return Runs(mock_client)


def test_create_run_returns_the_new_id(runs, mock_client):
    mock_client.call.return_value = {"id": 41, "projectPipelineId": 41}
    assert runs.create_run(3, 7, "r1") == 41
    mock_client.call.assert_called_once_with(
        "POST", "/api/v1/run/new-run-attempt", data={"pipelineId": 3, "projectId": 7, "name": "r1"}
    )


def test_create_run_accepts_an_older_server(runs, mock_client):
    mock_client.call.return_value = {"projectPipelineId": 42}
    assert runs.create_run(3, 7, "r1") == 42


def test_create_run_without_an_id_raises(runs, mock_client):
    mock_client.call.return_value = {}
    with pytest.raises(RuntimeError):
        runs.create_run(3, 7, "r1")


def test_save_run_sends_only_given_fields(runs, mock_client):
    runs.save_run(41, permission=3, run_environment_id=550, launch_directory="/home/jdoe/foundry-connect-runs/r1")
    mock_client.call.assert_called_once_with(
        "PATCH", "/api/v1/run/41/save",
        data={"permission": 3, "runEnvironmentId": 550, "launchDirectory": "/home/jdoe/foundry-connect-runs/r1"},
    )


def test_launch_run(runs, mock_client):
    runs.launch_run(41)
    mock_client.call.assert_called_once_with(
        "POST", "/api/v1/run/initiate-run", data={"runId": 41, "runType": "newrun"}
    )


def test_list_pipelines_reads_all_readable(runs, mock_client):
    runs.list_pipelines(search="rna", limit=5)
    mock_client.call.assert_called_once_with(
        "GET", "/api/v1/pipeline/", params={"type": "1,2,3,4", "take": 5, "searchKeyword": "rna"}
    )


def test_list_and_create_projects(runs, mock_client):
    runs.list_projects(name="P", limit=3)
    mock_client.call.assert_called_with("GET", "/api/v1/project/", params={"type": "1", "take": 3, "name": "P"})
    runs.create_project("New", summary="s")
    mock_client.call.assert_called_with("POST", "/api/v1/project/", data={"name": "New", "summary": "s"})


def test_form_and_status_read_the_run(runs, mock_client):
    runs.get_run_form(41)
    mock_client.call.assert_called_with("GET", "/api/v1/run/41/details")
    runs.run_status(41)
    mock_client.call.assert_called_with("GET", "/api/v1/run/41/status")


@pytest.mark.parametrize("name,expected", [
    ("RNA seq 1", "/home/jdoe/foundry-connect-runs/RNA_seq_1"),
    ("../../etc", "/home/jdoe/foundry-connect-runs/_.._etc"),
    ("", "/home/jdoe/foundry-connect-runs/run"),
])
def test_default_directory_home_pattern(name, expected):
    assert default_execution_directory(ENV, name) == expected


def test_default_directory_declared_wins():
    assert default_execution_directory({**ENV, "defWorkdir": "/lab/runs"}, "r") == "/lab/runs"


@pytest.mark.parametrize("user", [None, "", "a/b"])
def test_default_directory_none_without_login(user):
    assert default_execution_directory({**ENV, "username": user}, "r") is None


def test_client_exposes_runs(client):
    assert isinstance(client.runs, Runs)
    assert client.runs.client is client
