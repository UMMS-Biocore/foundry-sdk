import json
from unittest.mock import Mock

import pytest

from viafoundry.pipelines import (
    DEFAULT_PIPE_CONFIG,
    PipelineBuilder,
    PipelineGraphError,
    Pipelines,
    parse_edge,
    parse_nodes,
)


def _param(pid, name, file_type, qualifier, sname=None):
    return {"parameter_id": pid, "name": name, "file_type": file_type, "qualifier": qualifier, "sname": sname or name}


# Slot lists as GET /api/v1/process/{id} returned them on 2026-10-19.
PROCESSES = {
    3017: {"name": "gpu_smoke_check",
           "inputs": [_param(252, "text", "text", "val", "label")],
           "outputs": [_param(201, "outputFileTxt", "txt", "file", '"gpu_check.txt"')]},
    2357: {"name": "Xenium_Download_Dataset",
           "inputs": [_param(639, "samplesheet", "samplesheet", "set")],
           "outputs": [_param(131, "outputDir", "directory", "set")]},
    2356: {"name": "Xenium_Data_Analysis",
           "inputs": [_param(637, "inputDir", "directory", "set"),
                      _param(547, "inputFileTsv", "tsv", "file", "metadatasheet"),
                      _param(638, "inputFileTsv", "tsv", "set", "cellstats")],
           "outputs": [_param(385, "rdsFile", "RDS", "file"), _param(164, "outputHTML", "html", "file")]},
}

# Pipeline 1777 as the editor saved it.
DETAILS_1777 = {
    "updateAllowed": True,
    "pipeline": {"main_pipeline_1777": {
        "id": 1777, "name": "GPU smoke check (bootcamp)", "summary": "s", "description": "",
        "pipeline_group_id": 667, "pipeline_type": "ViaFoundry", "version": "1.0.0",
        "rev_comment": "Initial Version", "perms": 3, "pin": "false", "publicly_searchable": "false",
        "script_pipe_config": DEFAULT_PIPE_CONFIG, "script_pipe_header": "", "script_pipe_footer": "",
        "script_mode_header": "groovy", "script_mode_footer": "groovy",
        "publish_web_dir": "", "publish_web_app_dir": "", "publish_dmeta_dir": "",
        "nodes": json.dumps({"g-1": [354.6, 389, "3017", "gpu_smoke_check", {}],
                             "g-2": [82.3, 453.7, "inPro", "inputParam", {}],
                             "g-3": [768.0, 453.7, "outPro", "outputParam", {}]}),
        "edges": json.dumps({"edges": ["o-inPro-1-252-2_i-3017-0-252-1", "i-outPro-1-201-3_o-3017-0-201-1"]}),
        "mainG": json.dumps({"mainG": [61.9, 72.4, 0.7]}),
    }},
}

EDGES_1545 = [
    "o-2357-0-131-5_i-2356-0-637-0", "o-inPro-1-639-7_i-2357-0-639-5", "o-inPro-1-638-9_i-2356-1-547-0",
    "o-inPro-1-638-9_i-2356-2-638-0", "i-outPro-1-164-4_o-2356-1-164-0", "i-outPro-1-385-3_o-2356-0-385-0",
]
NODES_1545 = {"g-0": [0, 0, "2356", "Xenium_Data_Analysis", {}], "g-3": [0, 0, "outPro", "Analysis_Results_RDS", {"pubWeb": "rdata"}],
              "g-4": [0, 0, "outPro", "HTML_Report", {"pubWeb": "html"}], "g-5": [0, 0, "2357", "Xenium_Download_Dataset", {}],
              "g-7": [0, 0, "inPro", "samplesheet", {}], "g-9": [0, 0, "inPro", "metadatasheet", {}]}


@pytest.fixture
def builder():
    return PipelineBuilder(lambda pid: PROCESSES[pid])


def _shape(nodes, edges):
    """Edges with node keys replaced by node names, so graphs numbered differently compare equal."""
    name = {k: n["nodeName"] for k, n in nodes.items()}
    shaped = set()
    for edge in edges:
        src, dst = parse_edge(edge)
        shaped.add((name[src["node"]], src["param"], src["slot"], src["parameterId"],
                    name[dst["node"]], dst["param"], dst["slot"], dst["parameterId"]))
    return shaped


def test_builder_reproduces_1777_exactly(builder):
    proc = builder.add_process(3017)
    inp = builder.add_input("inputParam")
    out = builder.add_output("outputParam")
    builder.connect(inp, proc)
    builder.connect(proc, out)
    saved = parse_nodes(DETAILS_1777["pipeline"]["main_pipeline_1777"]["nodes"])
    assert builder.edges == ["o-inPro-1-252-2_i-3017-0-252-1", "i-outPro-1-201-3_o-3017-0-201-1"]
    assert {k: (n["param"], n["nodeName"]) for k, n in builder.nodes.items()} == \
        {k: (n["param"], n["nodeName"]) for k, n in saved.items()}


def test_builder_reproduces_1545_graph(builder):
    download = builder.add_process(2357)
    analysis = builder.add_process(2356)
    samples = builder.add_input("samplesheet")
    meta = builder.add_input("metadatasheet")
    rds = builder.add_output("Analysis_Results_RDS", publish="rdata")
    html = builder.add_output("HTML_Report", publish="html")
    builder.connect(download, analysis, input="inputDir")
    builder.connect(samples, download)
    builder.connect(meta, analysis, input=2)  # first target sets the input's parameter id (638)
    builder.connect(meta, analysis, input="metadatasheet")
    builder.connect(analysis, html, output="outputHTML")
    builder.connect(analysis, rds, output=385)
    assert _shape(builder.nodes, builder.edges) == _shape(parse_nodes(json.dumps(NODES_1545)), EDGES_1545)
    assert builder.nodes[rds]["nodeSettings"] == {"pubWeb": "rdata"}


def test_input_takes_the_first_targets_parameter_id(builder):
    analysis = builder.add_process(2356)
    meta = builder.add_input("metadatasheet")
    builder.connect(meta, analysis, input=2)
    second = builder.connect(meta, analysis, input=1)
    assert second.startswith("o-inPro-1-638-")


def test_type_mismatch_is_refused(builder):
    smoke = builder.add_process(3017)
    analysis = builder.add_process(2356)
    with pytest.raises(PipelineGraphError, match="wants"):
        builder.connect(smoke, analysis, input="inputDir")


def test_input_feeding_two_types_is_refused(builder):
    download = builder.add_process(2357)
    analysis = builder.add_process(2356)
    inp = builder.add_input("x")
    builder.connect(inp, download)
    with pytest.raises(PipelineGraphError):
        builder.connect(inp, analysis, input="inputDir")


def test_ambiguous_slot_must_be_named(builder):
    analysis = builder.add_process(2356)
    with pytest.raises(PipelineGraphError, match="name the one"):
        builder.connect(builder.add_input("x"), analysis)


def test_slot_cannot_take_two_edges(builder):
    download = builder.add_process(2357)
    builder.connect(builder.add_input("a"), download)
    with pytest.raises(PipelineGraphError, match="already connected"):
        builder.connect(builder.add_input("b"), download)


def test_same_edge_twice_is_kept_once(builder):
    smoke = builder.add_process(3017)
    inp = builder.add_input("in")
    builder.connect(inp, smoke)
    builder.connect(inp, smoke)
    assert len(builder.edges) == 1


@pytest.mark.parametrize("direction", ["out_to_proc", "in_to_out"])
def test_wrong_direction_is_refused(builder, direction):
    smoke = builder.add_process(3017)
    inp, out = builder.add_input("in"), builder.add_output("out")
    with pytest.raises(PipelineGraphError):
        if direction == "out_to_proc":
            builder.connect(out, smoke)
        else:
            builder.connect(inp, out)


def test_get_pipeline_parses_graph_fields():
    client = Mock()
    client.call.return_value = DETAILS_1777
    p = Pipelines(client).get_pipeline(1777)
    client.call.assert_called_once_with("GET", "/api/pipeline/v1/1777/details")
    assert p["nodes"]["g-2"] == {"nodeName": "inputParam", "xCoordinate": 82.3, "yCoordinate": 453.7, "param": "inPro", "nodeSettings": {}}
    assert p["edges"][0] == "o-inPro-1-252-2_i-3017-0-252-1"
    assert p["mainG"] == [61.9, 72.4, 0.7]


def test_create_pipeline_is_private_by_default():
    client = Mock()
    Pipelines(client).create_pipeline("P", 667, nodes={"g-1": {}}, edges=["e"])
    method, endpoint = client.call.call_args.args
    body = client.call.call_args.kwargs["data"]
    assert (method, endpoint) == ("POST", "/api/pipeline/v1")
    assert "id" not in body
    assert body["permission"] == 3 and body["pipelineGroupId"] == 667
    assert body["nodes"] == {"g-1": {}} and body["edges"] == ["e"]


def test_update_pipeline_resends_unchanged_fields():
    client = Mock()
    client.call.side_effect = [DETAILS_1777, {"id": 1777}]
    Pipelines(client).update_pipeline(1777, name="Renamed")
    body = client.call.call_args.kwargs["data"]
    assert body["id"] == 1777 and body["name"] == "Renamed"
    assert body["pipelineGroupId"] == 667 and body["permission"] == 3
    assert body["scriptPipeConfig"] == DEFAULT_PIPE_CONFIG
    assert body["edges"] == ["o-inPro-1-252-2_i-3017-0-252-1", "i-outPro-1-201-3_o-3017-0-201-1"]
    assert body["nodes"]["g-1"]["param"] == "3017"


def test_update_pipeline_refuses_unknown_fields():
    client = Mock()
    client.call.return_value = DETAILS_1777
    with pytest.raises(ValueError, match="pipeline_group_id"):
        Pipelines(client).update_pipeline(1777, pipeline_group_id=1)
    assert client.call.call_count == 1


def test_builder_from_saved_pipeline_numbers_after_existing():
    client = Mock()
    client.call.side_effect = lambda method, endpoint, **kw: DETAILS_1777 if "details" in endpoint else PROCESSES[3017]
    b = Pipelines(client).builder(1777)
    assert b.add_output("second") == "g-4"


def test_client_exposes_pipelines(client):
    assert isinstance(client.pipelines, Pipelines)
