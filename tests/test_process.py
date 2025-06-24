import pytest
from unittest.mock import Mock, MagicMock, patch
from viafoundry.process import Process
from viafoundry.models.domain.process import (
    ProcessSummaryResponse,
    ProcessResponse,
    ProcessConfig,
    ServerParameterResponse,
    Parameter,
)


@pytest.fixture
def mock_client():
    return Mock()


@pytest.fixture
def process(mock_client):
    return Process(mock_client)


def test_list_processes_success(process, mock_client):
    mock_client.call.return_value = {
        "data": [{"id": 1, "name": "proc", "summary": "s"}]}
    with patch("viafoundry.process.TypeAdapter") as ta:
        ta.return_value.validate_python.return_value = [
            ProcessSummaryResponse(id=1, name="proc", summary="s")
        ]
        result = process.list_processes()
        assert isinstance(result, list)
        assert result[0].id == 1
        assert result[0].name == "proc"
        assert result[0].summary == "s"


def test_list_processes_failure(process, mock_client):
    mock_client.call.side_effect = Exception("fail")
    with pytest.raises(Exception) as e:
        process.list_processes()
    assert "Failed to list processes" in str(e.value)


def test_get_process_success(process, mock_client):
    mock_client.call.return_value = {
        "id": 1, "name": "proc", "process_group_id": 1}
    with patch("viafoundry.process.TypeAdapter") as ta:
        ta.return_value.validate_python.return_value = ProcessResponse(
            id=1, name="proc", process_group_id=1)
        result = process.get_process("1")
        assert result.id == 1
        assert result.name == "proc"


def test_get_process_failure(process, mock_client):
    mock_client.call.side_effect = Exception("fail")
    with pytest.raises(Exception) as e:
        process.get_process("1")
    assert "Failed to retrieve process" in str(e.value)


def test_get_process_revisions_success(process, mock_client):
    mock_client.call.return_value = {"revisions": [
        {"id": 1, "name": "rev", "process_group_id": 1}]}
    with patch("viafoundry.process.TypeAdapter") as ta:
        ta.return_value.validate_python.return_value = [
            ProcessResponse(id=1, name="rev", process_group_id=1)
        ]
        result = process.get_process_revisions("1")
        assert isinstance(result, list)
        assert result[0].id == 1


def test_duplicate_process_success(process, mock_client):
    mock_client.call.return_value = {
        "id": 2, "name": "dup", "process_group_id": 1}
    with patch("viafoundry.process.TypeAdapter") as ta:
        ta.return_value.validate_python.return_value = ProcessResponse(
            id=2, name="dup", process_group_id=1)
        result = process.duplicate_process("1")
        assert result.id == 2
        assert result.name == "dup"


def test_create_menu_group_success(process, mock_client):
    mock_client.call.return_value = {"id": 10, "name": "group"}
    result = process.create_menu_group("group")
    assert result["id"] == 10
    assert result["name"] == "group"


def test_list_menu_groups_success(process, mock_client):
    mock_client.call.return_value = {"data": [{"id": 1, "name": "g"}]}
    result = process.list_menu_groups()
    assert "data" in result
    assert result["data"][0]["name"] == "g"


def test_update_menu_group_success(process, mock_client):
    mock_client.call.return_value = {"id": 1, "name": "new"}
    result = process.update_menu_group("1", "new")
    assert result["name"] == "new"


def test_create_process_success(process, mock_client):
    mock_client.call.return_value = {
        "id": 1, "name": "proc", "process_group_id": 1}
    with patch("viafoundry.process.TypeAdapter") as ta:
        ta.return_value.validate_python.return_value = ProcessResponse(
            id=1, name="proc", process_group_id=1)
        dummy_config = MagicMock(spec=ProcessConfig)
        dummy_config.model_dump.return_value = {"name": "proc"}
        result = process.create_process(dummy_config)
        assert result.id == 1


def test_update_process_success(process, mock_client):
    mock_client.call.return_value = {
        "id": 1, "name": "proc", "process_group_id": 1}
    with patch("viafoundry.process.TypeAdapter") as ta:
        ta.return_value.validate_python.return_value = ProcessResponse(
            id=1, name="proc", process_group_id=1)
        dummy_config = MagicMock(spec=ProcessConfig)
        dummy_config.model_dump.return_value = {"name": "proc"}
        result = process.update_process("1", dummy_config)
        assert result.id == 1


def test_delete_process_success(process, mock_client):
    mock_client.call.return_value = None
    assert process.delete_process("1") is None


def test_list_parameters_success(process, mock_client):
    mock_client.call.return_value = [
        {"id": 1, "name": "p", "qualifier": "val", "fileType": None}
    ]
    with patch("viafoundry.process.TypeAdapter") as ta:
        ta.return_value.validate_python.return_value = [
            ServerParameterResponse(
                id=1, name="p", qualifier="val", fileType=None)
        ]
        result = process.list_parameters()
        assert isinstance(result, list)
        assert result[0].id == 1


def test_create_parameter_success(process, mock_client):
    mock_client.call.return_value = {
        "id": 1, "name": "p", "qualifier": "val", "fileType": None
    }
    with patch("viafoundry.process.TypeAdapter") as ta:
        ta.return_value.validate_python.return_value = ServerParameterResponse(
            id=1, name="p", qualifier="val", fileType=None)
        dummy_param = MagicMock(spec=Parameter)
        dummy_param.model_dump.return_value = {"name": "p"}
        result = process.create_parameter(dummy_param)
        assert result.id == 1


def test_update_parameter_success(process, mock_client):
    mock_client.call.return_value = {
        "id": 1, "name": "p", "qualifier": "val", "fileType": None
    }
    with patch("viafoundry.process.TypeAdapter") as ta:
        ta.return_value.validate_python.return_value = ServerParameterResponse(
            id=1, name="p", qualifier="val", fileType=None)
        dummy_param = MagicMock(spec=Parameter)
        dummy_param.model_dump.return_value = {"name": "p"}
        result = process.update_parameter("1", dummy_param)
        assert result.id == 1


def test_delete_parameter_success(process, mock_client):
    mock_client.call.return_value = None
    assert process.delete_parameter("1") is None


def test_get_menu_group_by_name_found(process, mock_client):
    mock_client.call.return_value = {"data": [{"id": 5, "name": "foo"}]}
    result = process.get_menu_group_by_name("foo")
    assert result == 5


def test_get_menu_group_by_name_not_found(process, mock_client):
    mock_client.call.return_value = {"data": [{"id": 5, "name": "foo"}]}
    result = process.get_menu_group_by_name("bar")
    assert result is None


def test_filter_parameters_filters(process, mock_client):
    class DummyParam:
        def __init__(self, id, name, qualifier, fileType):
            self.id = id
            self.name = name
            self.qualifier = qualifier
            self.fileType = fileType
    mock_client.call.return_value = [DummyParam(
        1, "foo", "q", "txt"), DummyParam(2, "bar", "q2", "csv")]
    process.list_parameters = lambda: mock_client.call.return_value
    filtered = process.filter_parameters(name="foo")
    assert len(filtered) == 1
    assert filtered[0].name == "foo"
    filtered = process.filter_parameters(qualifier="q2")
    assert len(filtered) == 1
    assert filtered[0].name == "bar"
    filtered = process.filter_parameters(fileType="csv")
    assert len(filtered) == 1
    assert filtered[0].name == "bar"
    filtered = process.filter_parameters(id_="1")
    assert len(filtered) == 1
    assert filtered[0].name == "foo"


def test_create_process_config_creates_menu_group_if_missing(process, mock_client):
    process.get_menu_group_by_name = lambda name: None
    process.create_menu_group = lambda name: {"id": 42}
    process.filter_parameters = lambda **kwargs: [
        type("P", (), {"id": 1, "name": "foo", "qualifier": None, "fileType": None})()]
    input_params = [{"name": "foo", "qualifier": None, "fileType": None, "displayName": "foo",
                     "operator": "", "operatorContent": "", "optional": False, "test": ""}]
    output_params = [{"name": "foo", "qualifier": None, "fileType": None, "displayName": "foo",
                      "operator": "", "operatorContent": "", "optional": False, "test": ""}]
    config = process.create_process_config(
        name="proc",
        menu_group_name="group",
        input_params=input_params,
        output_params=output_params,
    )
    assert config.menuGroupId == 42
    assert config.inputParameters[0].displayName == "foo"


def test_create_process_config_with_existing_menu_group(process, mock_client):
    process.get_menu_group_by_name = lambda name: 99
    process.create_menu_group = lambda name: {"id": 99}
    process.filter_parameters = lambda **kwargs: [
        type("P", (), {"id": 2, "name": "bar", "qualifier": None, "fileType": None})()]
    input_params = [{"name": "bar", "qualifier": None, "fileType": None, "displayName": "bar",
                     "operator": "", "operatorContent": "", "optional": True, "test": "t"}]
    output_params = [{"name": "bar", "qualifier": None, "fileType": None, "displayName": "bar",
                      "operator": "", "operatorContent": "", "optional": True, "test": "t"}]
    config = process.create_process_config(
        name="proc2",
        menu_group_name="group2",
        input_params=input_params,
        output_params=output_params,
        summary="summary",
        script_body="echo hi",
        script_language="bash",
        script_header="# header",
        script_footer="# footer",
        permission_settings={"viewPermissions": 3, "writeGroupIds": [1, 2]},
        revision_comment="rev"
    )
    assert config.menuGroupId == 99
    assert config.inputParameters[0].displayName == "bar"
    assert config.inputParameters[0].optional is True
    assert config.inputParameters[0].test == "t"
    assert config.script.body == "echo hi"
    assert config.script.header == "# header"
    assert config.script.footer == "# footer"
    assert config.script.language == "bash"
    assert config.permissionSettings.viewPermissions == 3
    assert config.revisionComment == "rev"


def test_create_process_config_with_new_parameter(process, mock_client):
    """
    Test creating a process config where the parameter does not exist and must be created.
    """
    # Simulate filter_parameters returns empty, so create_parameter is called
    created_param = type(
        "P", (), {"id": 123, "name": "newparam", "qualifier": "val", "fileType": None})()
    # First call returns [], second call returns [created_param]
    process.filter_parameters = MagicMock(
        side_effect=[[], [created_param], [], [created_param]])
    process.create_menu_group = lambda name: {"id": 55}
    process.get_menu_group_by_name = lambda name: 55
    process.create_parameter = MagicMock(return_value=ServerParameterResponse(
        id=123, name="newparam", qualifier="val", fileType=None))
    input_params = [{
        "name": "newparam",
        "qualifier": "val",
        "fileType": None,
        "displayName": "New Param",
        "operator": "",
        "operatorContent": "",
        "optional": False,
        "test": "testval"
    }]
    output_params = [{
        "name": "newparam",
        "qualifier": "val",
        "fileType": None,
        "displayName": "New Param",
        "operator": "",
        "operatorContent": "",
        "optional": False,
        "test": "testval"
    }]
    config = process.create_process_config(
        name="proc3",
        menu_group_name="group3",
        input_params=input_params,
        output_params=output_params,
        summary="summary",
        script_body="echo hi",
        script_language="bash",
        script_header="# header",
        script_footer="# footer",
        permission_settings={"viewPermissions": 3, "writeGroupIds": [1, 2]},
        revision_comment="rev"
    )
    assert config.menuGroupId == 55
    assert config.inputParameters[0].displayName == "New Param"
    assert config.inputParameters[0].parameterId == 123
    assert config.inputParameters[0].test == "testval"
    assert config.outputParameters[0].parameterId == 123
    assert process.create_parameter.called


def test_create_process_config_menu_group_created_if_missing(process, mock_client):
    """
    Test that menu group is created if not found.
    """
    process.get_menu_group_by_name = MagicMock(return_value=None)
    process.create_menu_group = MagicMock(return_value={"id": 77})
    process.filter_parameters = MagicMock(return_value=[
        type("P", (), {"id": 5, "name": "foo",
             "qualifier": None, "fileType": None})()
    ])
    input_params = [{
        "name": "foo",
        "qualifier": None,
        "fileType": None,
        "displayName": "foo",
        "operator": "",
        "operatorContent": "",
        "optional": False,
        "test": ""
    }]
    output_params = [{
        "name": "foo",
        "qualifier": None,
        "fileType": None,
        "displayName": "foo",
        "operator": "",
        "operatorContent": "",
        "optional": False,
        "test": ""
    }]
    config = process.create_process_config(
        name="proc4",
        menu_group_name="group4",
        input_params=input_params,
        output_params=output_params,
    )
    assert config.menuGroupId == 77
    process.create_menu_group.assert_called_once_with("group4")


def test_filter_parameters_multiple_filters(process, mock_client):
    """
    Test filter_parameters with multiple filters applied.
    """
    class DummyParam:
        def __init__(self, id, name, qualifier, fileType):
            self.id = id
            self.name = name
            self.qualifier = qualifier
            self.fileType = fileType
    params = [
        DummyParam(1, "foo", "q", "txt"),
        DummyParam(2, "bar", "q2", "csv"),
        DummyParam(3, "baz", "q", "csv"),
    ]
    process.list_parameters = lambda: params
    filtered = process.filter_parameters(
        name="ba", qualifier="q", fileType="csv")
    assert len(filtered) == 1
    assert filtered[0].name == "baz"
    mock_client.call.side_effect = Exception("fail")
    with pytest.raises(Exception) as e:
        process.create_menu_group("failgroup")
    assert "Failed to create menu group" in str(e.value)


def test_update_menu_group_failure(process, mock_client):
    mock_client.call.side_effect = Exception("fail")
    with pytest.raises(Exception) as e:
        process.update_menu_group("1", "failname")
    assert "Failed to update menu group" in str(e.value)


def test_delete_process_failure(process, mock_client):
    mock_client.call.side_effect = Exception("fail")
    with pytest.raises(Exception) as e:
        process.delete_process("1")
    assert "Failed to delete process" in str(e.value)


def test_list_parameters_failure(process, mock_client):
    mock_client.call.side_effect = Exception("fail")
    with pytest.raises(Exception) as e:
        process.list_parameters()
    assert "Failed to list parameters" in str(e.value)


def test_create_parameter_failure(process, mock_client):
    mock_client.call.side_effect = Exception("fail")
    dummy_param = MagicMock(spec=Parameter)
    dummy_param.model_dump.return_value = {"name": "p"}
    with pytest.raises(Exception) as e:
        process.create_parameter(dummy_param)
    assert "Failed to create a new parameter" in str(e.value)


def test_update_parameter_failure(process, mock_client):
    mock_client.call.side_effect = Exception("fail")
    dummy_param = MagicMock(spec=Parameter)
    dummy_param.model_dump.return_value = {"name": "p"}
    with pytest.raises(Exception) as e:
        process.update_parameter("1", dummy_param)
    assert "Failed to update parameter with ID 1" in str(e.value)


def test_delete_parameter_failure(process, mock_client):
    mock_client.call.side_effect = Exception("fail")
    with pytest.raises(Exception) as e:
        process.delete_parameter("1")
    assert "Failed to delete parameter with ID 1" in str(e.value)


def test_list_menu_groups_failure(process, mock_client):
    mock_client.call.side_effect = Exception("fail")
    with pytest.raises(Exception) as e:
        process.list_menu_groups()
    assert "Failed to list menu groups" in str(e.value)
