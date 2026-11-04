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


# Modules: another pipeline used as a node, param "p<pipeline id>". Its edge
# ends are pi-<inner process>-<port order>-<inner parameter>-<N> and po-...,
# numbered as the backend's module-ports.ts numbers them.

def _pipeline_details(pipeline_id, name, nodes, edges):
    """Details as GET /api/pipeline/v1/{id}/details returns them."""
    saved = dict(DETAILS_1777["pipeline"]["main_pipeline_1777"], id=pipeline_id, name=name,
                 nodes=json.dumps(nodes), edges=json.dumps({"edges": edges}))
    return {"updateAllowed": True, "pipeline": {f"main_pipeline_{pipeline_id}": saved}}


MODULE_PROCESSES = {
    **PROCESSES,
    9001: {"name": "make_sheet", "inputs": [],
           "outputs": [_param(901, "sheet", "samplesheet", "set")]},
    9002: {"name": "show_html", "inputs": [_param(902, "page", "html", "file")],
           "outputs": [_param(903, "shown", "html", "file")]},
}

# Pipeline 1800 uses 1777 as a module on g-1, as the editor saved it.
NODES_1800 = {"g-1": [300, 400, "p1777", "GPU smoke module", {}], "g-2": [80, 450, "inPro", "label", {}],
              "g-3": [700, 450, "outPro", "report", {}]}
EDGES_1800 = ["o-inPro-1-252-2_pi-3017-0-252-1", "i-outPro-1-201-3_po-3017-0-201-1"]

# Pipeline 1900 takes an html page into process 9002, so a 1545 module output can feed it.
NODES_1900 = {"g-1": [0, 0, "9002", "show_html", {}], "g-2": [0, 0, "inPro", "page", {}],
              "g-3": [0, 0, "outPro", "shown", {}]}
EDGES_1900 = ["o-inPro-1-902-2_i-9002-0-902-1", "i-outPro-1-903-3_o-9002-0-903-1"]


def _pipelines(extra=None):
    """Pipeline id -> pipeline as Pipelines.get_pipeline returns it."""
    details = {
        1777: DETAILS_1777,
        1545: _pipeline_details(1545, "Xenium", NODES_1545, EDGES_1545),
        1800: _pipeline_details(1800, "Uses a module", NODES_1800, EDGES_1800),
        1900: _pipeline_details(1900, "Show html", NODES_1900, EDGES_1900),
        **(extra or {}),
    }
    return {pid: Pipelines(Mock(call=Mock(return_value=d))).get_pipeline(pid) for pid, d in details.items()}


@pytest.fixture
def modular():
    pipelines = _pipelines()
    return PipelineBuilder(lambda pid: MODULE_PROCESSES[pid], get_pipeline=lambda pid: pipelines[pid])


@pytest.mark.parametrize("edge,source,target", [
    ("o-inPro-1-252-2_pi-3017-0-252-1", "o", "pi"),
    ("pi-3017-0-252-1_o-inPro-1-252-2", "o", "pi"),
    ("i-outPro-1-201-3_po-3017-0-201-1", "po", "i"),
    ("po-3017-0-201-1_i-outPro-1-201-3", "po", "i"),
    ("pi-9002-0-902-4_po-2356-0-164-1", "po", "pi"),
])
def test_parse_edge_puts_module_ends_in_dataflow_order(edge, source, target):
    src, dst = parse_edge(edge)
    assert (src["side"], dst["side"]) == (source, target)


def test_module_ports_follow_the_backend_numbering(modular):
    # One input per distinct inPro end in first appearance order, carrying the
    # last consumer (g-9 feeds 547 then 638); one output per outPro edge in order.
    assert modular.module_ports(1545) == {
        "inputs": [
            {"slot": 0, "name": "samplesheet", "process_id": 2357, "parameter_id": 639,
             "file_type": "samplesheet", "qualifier": "set"},
            {"slot": 1, "name": "metadatasheet", "process_id": 2356, "parameter_id": 638,
             "file_type": "tsv", "qualifier": "set"},
        ],
        "outputs": [
            {"slot": 0, "name": "HTML_Report", "process_id": 2356, "parameter_id": 164,
             "file_type": "html", "qualifier": "file"},
            {"slot": 1, "name": "Analysis_Results_RDS", "process_id": 2356, "parameter_id": 385,
             "file_type": "RDS", "qualifier": "file"},
        ],
    }


def test_module_ports_of_a_nested_module_take_types_from_the_inner_process(modular):
    ports = modular.module_ports(1800)
    assert [(p["name"], p["process_id"], p["parameter_id"], p["file_type"], p["qualifier"]) for p in ports["inputs"]] == \
        [("label", 3017, 252, "text", "val")]
    assert [(p["name"], p["process_id"], p["parameter_id"], p["file_type"]) for p in ports["outputs"]] == \
        [("report", 3017, 201, "txt")]


def test_add_module_names_the_node_after_the_pipeline(modular):
    node = modular.add_module(1777)
    assert modular.nodes[node]["param"] == "p1777"
    assert modular.nodes[node]["nodeName"] == "GPU smoke check (bootcamp)"
    assert modular.nodes[modular.add_module(1777, name="again", x=5, y=6)]["nodeName"] == "again"


def test_builder_reproduces_1800_exactly(modular):
    module = modular.add_module(1777, name="GPU smoke module")
    label, report = modular.add_input("label"), modular.add_output("report")
    modular.connect(label, module)
    modular.connect(module, report)
    assert modular.edges == EDGES_1800
    assert {k: (n["param"], n["nodeName"]) for k, n in modular.nodes.items()} == \
        {k: (n[2], n[3]) for k, n in NODES_1800.items()}


def test_module_ports_are_picked_by_name_or_slot(modular):
    module = modular.add_module(1545)  # g-1
    sheet, meta = modular.add_input("sheet"), modular.add_input("meta")  # g-2, g-3
    rds = modular.add_output("rds")  # g-4
    assert modular.connect(sheet, module, input="samplesheet") == "o-inPro-1-639-2_pi-2357-0-639-1"
    assert modular.connect(meta, module, input=1) == "o-inPro-1-638-3_pi-2356-1-638-1"
    assert modular.connect(module, rds, output="Analysis_Results_RDS") == "i-outPro-1-385-4_po-2356-1-385-1"


def test_process_to_module_module_to_process_and_module_to_module(modular):
    make = modular.add_process(9001)  # g-1
    xenium = modular.add_module(1545)  # g-2
    show = modular.add_process(9002)  # g-3
    page = modular.add_module(1900)  # g-4
    assert modular.connect(make, xenium, input=0) == "o-9001-0-901-1_pi-2357-0-639-2"
    assert modular.connect(xenium, show, output="HTML_Report") == "po-2356-0-164-2_i-9002-0-902-3"
    assert modular.connect(xenium, page, output=0) == "po-2356-0-164-2_pi-9002-0-902-4"


def test_a_module_port_of_another_type_is_refused(modular):
    smoke = modular.add_process(3017)
    xenium = modular.add_module(1545)
    with pytest.raises(PipelineGraphError, match="wants"):
        modular.connect(smoke, xenium, input="samplesheet")


def test_an_unknown_module_port_is_refused(modular):
    xenium = modular.add_module(1545)
    with pytest.raises(PipelineGraphError, match="no input matching 'nope'"):
        modular.connect(modular.add_input("x"), xenium, input="nope")
    with pytest.raises(PipelineGraphError, match="name the one"):
        modular.connect(modular.add_input("y"), xenium)


def test_a_module_input_takes_one_edge(modular):
    module = modular.add_module(1777)
    modular.connect(modular.add_input("a"), module)
    with pytest.raises(PipelineGraphError, match="already connected"):
        modular.connect(modular.add_input("b"), module)


def test_an_input_feeding_a_module_cannot_also_feed_another_type():
    pipelines = _pipelines()
    b = PipelineBuilder(lambda pid: MODULE_PROCESSES[pid], parse_nodes(json.dumps(NODES_1800)), list(EDGES_1800),
                        get_pipeline=lambda pid: pipelines[pid])
    smoke = b.add_process(3017)
    assert b.connect("g-2", smoke).startswith("o-inPro-1-252-2_")
    with pytest.raises(PipelineGraphError):
        b.connect("g-2", b.add_process(2357))


def test_a_builder_without_get_pipeline_cannot_add_a_module(builder):
    with pytest.raises(PipelineGraphError, match="get_pipeline"):
        builder.add_module(1777)


def test_an_unreadable_module_is_refused():
    b = PipelineBuilder(lambda pid: PROCESSES[pid], get_pipeline=lambda pid: {})
    with pytest.raises(PipelineGraphError, match="could not be read"):
        b.add_module(42)


@pytest.mark.parametrize("own,module", [(1777, 1777), (1777, 1800)])
def test_a_module_that_holds_the_pipeline_being_built_is_refused(own, module):
    pipelines = _pipelines()
    b = PipelineBuilder(lambda pid: PROCESSES[pid], get_pipeline=lambda pid: pipelines[pid], pipeline_id=own)
    with pytest.raises(PipelineGraphError, match=f"pipeline {own}"):
        b.add_module(module)
    assert b.nodes == {}


def _chain(depth):
    """Pipelines 2001.. each holding the next as a module, the last holding 1777."""
    extra = {}
    for level in range(depth):
        pid = 2001 + level
        inner = 2002 + level if level < depth - 1 else 1777
        extra[pid] = _pipeline_details(pid, f"level {level}", {"g-1": [0, 0, f"p{inner}", "m", {}]}, [])
    return _pipelines(extra)


def test_modules_nest_five_deep_and_no_deeper():
    five = _chain(4)  # 2001 > 2002 > 2003 > 2004 > 1777: five modules deep under the new pipeline
    PipelineBuilder(lambda pid: PROCESSES[pid], get_pipeline=lambda pid: five[pid]).add_module(2001)
    six = _chain(5)
    with pytest.raises(PipelineGraphError, match="5"):
        PipelineBuilder(lambda pid: PROCESSES[pid], get_pipeline=lambda pid: six[pid]).add_module(2001)


def test_a_module_cycle_is_refused():
    cycle = _pipelines({
        2101: _pipeline_details(2101, "a", {"g-1": [0, 0, "p2102", "m", {}]}, []),
        2102: _pipeline_details(2102, "b", {"g-1": [0, 0, "p2101", "m", {}]}, []),
    })
    with pytest.raises(PipelineGraphError, match="itself"):
        PipelineBuilder(lambda pid: PROCESSES[pid], get_pipeline=lambda pid: cycle[pid]).add_module(2101)


def test_pipelines_builder_reads_modules_and_knows_its_own_id():
    details = {1777: DETAILS_1777, 1800: _pipeline_details(1800, "Uses a module", NODES_1800, EDGES_1800)}
    client = Mock()
    client.call.side_effect = lambda method, endpoint, **kw: \
        details[int(endpoint.split("/")[-2])] if "details" in endpoint else PROCESSES[int(endpoint.rsplit("/", 1)[1])]
    assert Pipelines(client).builder().add_module(1777) == "g-1"
    with pytest.raises(PipelineGraphError, match="pipeline 1777"):
        Pipelines(client).builder(1777).add_module(1800)
