"""Read, create and save pipelines, and build their graphs from code.

The web editor saves a pipeline with one call, POST /api/pipeline/v1: without
an id it creates, with an id it saves over that pipeline. A pipeline's graph is
a set of nodes and a list of edge strings.

A node is a process (its param is the process id), a pipeline input (``inPro``),
a pipeline output (``outPro``) or a module (``p<pipeline id>``), another
pipeline used as a node. Each end of an edge is a handle,
``{o|i}-{param}-{slot}-{parameterId}-{N}``: o for an output, i for an input,
slot the 0-based position among that process's inputs or outputs (always 1 on
inPro and outPro), parameterId the shared parameter definition, and N the
number in the node key ``g-N``. Edges run output to input, except that an edge
into a pipeline output is written outPro side first.

A module's edge ends are ``pi-{process}-{order}-{parameterId}-{N}`` (a module
input) and ``po-...`` (a module output): process and parameterId belong to the
process inside the module that consumes or produces the value, and order is
the port's 0-based position among the module's inputs or outputs. Ports are
numbered as the server numbers them: one input per distinct pipeline input end
in the module's edges, in first appearance order, carrying the last process it
feeds; one output per pipeline output edge, in stored order.

Process ids and pipeline ids are separate id spaces, and pipeline menu groups
are separate from process menu groups.
"""
import json
import re
from typing import Callable, Dict, List, Optional, Tuple, Union

INPUT_NODE = "inPro"
OUTPUT_NODE = "outPro"
MAX_MODULE_DEPTH = 5

_MODULE_PARAM = re.compile(r"^p(\d+)$")

DEFAULT_PIPE_CONFIG = (
    '\n//~@:~\n@~:"nextflow.config"\n//~@:~\n'
    'nextflow.enable.dsl=2\n'
    '$INITIAL_RUN_TYPE="gzip"\n'
    '    \n//* autofill\n'
    'if ($HOSTNAME == "default"){\n'
    '    $DOCKER_IMAGE = "quay.io/viascientific/pipeline_base_image:1.0"\n'
    '}\n//* autofill\n//~@:~\n'
)

# Saved field name -> field name in GET .../details, for fields a save resends.
_SAVE_FIELDS = {
    "name": "name",
    "summary": "summary",
    "description": "description",
    "pipelineGroupId": "pipeline_group_id",
    "pipelineType": "pipeline_type",
    "version": "version",
    "revComment": "rev_comment",
    "permission": "perms",
    "pin": "pin",
    "publiclySearchable": "publicly_searchable",
    "scriptPipeConfig": "script_pipe_config",
    "scriptPipeHeader": "script_pipe_header",
    "scriptPipeFooter": "script_pipe_footer",
    "scriptModeHeader": "script_mode_header",
    "scriptModeFooter": "script_mode_footer",
    "publishWebDir": "publish_web_dir",
    "publishWebAppDir": "publish_web_app_dir",
    "publishDMetaDir": "publish_dmeta_dir",
}


class PipelineGraphError(ValueError):
    """A node or edge the editor would refuse."""


def _json_field(value, key: Optional[str] = None):
    """Details return graph fields as JSON strings, sometimes wrapped in {key: ...}."""
    if isinstance(value, str):
        value = json.loads(value) if value.strip() else None
    if key and isinstance(value, dict) and key in value:
        value = value[key]
    return value


def parse_nodes(raw) -> Dict[str, Dict]:
    """Nodes from details ([x, y, param, name, settings] per key) in the saved shape."""
    nodes = {}
    for key, node in (_json_field(raw) or {}).items():
        if isinstance(node, dict):
            nodes[key] = node
            continue
        x, y, param, name = node[:4]
        nodes[key] = {
            "nodeName": name,
            "xCoordinate": x,
            "yCoordinate": y,
            "param": str(param),
            "nodeSettings": node[4] if len(node) > 4 and node[4] else {},
        }
    return nodes


def parse_handle(handle: str) -> Dict:
    """Split ``o-2357-0-131-5`` into its parts."""
    side, param, slot, parameter_id, number = handle.split("-")
    return {
        "side": side,
        "param": param,
        "slot": int(slot),
        "parameterId": int(parameter_id),
        "node": f"g-{number}",
    }


def parse_edge(edge: str) -> Tuple[Dict, Dict]:
    """(source output handle, target input handle) of an edge string, whatever its written order.

    Module ends (pi, po) count by their last letter, so they parse in dataflow order too.
    """
    first, second = (parse_handle(h) for h in edge.split("_"))
    return (first, second) if first["side"][-1] == "o" else (second, first)


def module_id(param) -> Optional[int]:
    """The pipeline id of a module node's param (``p1777``), or None for any other node."""
    match = _MODULE_PARAM.match(str(param))
    return int(match.group(1)) if match else None


def _module_io_ports(pipeline_id: int, edges: List[str]) -> Dict[str, List[Dict]]:
    """A module pipeline's ports as the server numbers them, from its edges alone."""
    inputs: Dict[str, Dict] = {}
    outputs: List[Dict] = []
    for edge in edges:
        halves = edge.split("_")
        parts = [half.split("-") for half in halves]
        if len(halves) != 2 or any(len(p) != 5 for p in parts):
            raise PipelineGraphError(f"Module pipeline {pipeline_id} has a malformed edge {edge}.")
        io_at = next((i for i, p in enumerate(parts) if p[1] in (INPUT_NODE, OUTPUT_NODE)), None)
        if io_at is None:
            continue
        io, other = parts[io_at], parts[1 - io_at]
        port = {"node": f"g-{io[4]}", "side": other[0], "process_id": int(other[1]),
                "process_slot": int(other[2]), "parameter_id": int(other[3])}
        if io[1] == INPUT_NODE:
            # A later edge from the same end keeps the port's place and takes its consumer.
            inputs[halves[io_at]] = port
        else:
            outputs.append(port)
    return {"inputs": list(inputs.values()), "outputs": outputs}


def _type_of(parameter: Dict) -> Tuple[str, str]:
    file_type = parameter.get("file_type") or parameter.get("fileType") or ""
    return file_type.lower(), parameter.get("qualifier") or ""


def compatible(output: Dict, input_: Dict) -> bool:
    """Whether a process output may feed a process input.

    Ends match on file type, not on parameter id: a directory set output feeds
    a directory set input with another parameter id (pipeline 1545). A value
    (qualifier val) connects only to a value.
    """
    out_type, out_qualifier = _type_of(output)
    in_type, in_qualifier = _type_of(input_)
    return out_type == in_type and (out_qualifier == "val") == (in_qualifier == "val")


class PipelineBuilder:
    """Assemble nodes and edges for create_pipeline or update_pipeline.

    ``get_process`` returns a process as GET /api/v1/process/{id} does, with its
    ``inputs`` and ``outputs`` lists; the builder reads slot order and types from it.
    ``get_pipeline`` returns a pipeline as Pipelines.get_pipeline does; the builder
    reads module pipelines with it. ``pipeline_id`` is the pipeline being built when
    it already has an id, and ``revision_ids`` its other revisions: a module that
    holds any of them, at any depth, is refused.
    """

    COLUMN = 250
    ROW = 120

    def __init__(
        self,
        get_process: Callable[[int], Dict],
        nodes: Optional[Dict] = None,
        edges: Optional[List[str]] = None,
        get_pipeline: Optional[Callable[[int], Dict]] = None,
        pipeline_id: Optional[int] = None,
        revision_ids: Optional[List[int]] = None,
    ) -> None:
        self._get_process = get_process
        self._get_pipeline = get_pipeline
        self._own_ids = {int(i) for i in [pipeline_id, *(revision_ids or [])] if i is not None}
        self._processes: Dict[str, Dict] = {}
        self._pipelines: Dict[int, Dict] = {}
        self._module_ports: Dict[int, Dict[str, List[Dict]]] = {}
        self.nodes: Dict[str, Dict] = dict(nodes or {})
        self.edges: List[str] = list(edges or [])

    def _next_key(self) -> str:
        numbers = [int(k.split("-")[1]) for k in self.nodes]
        return f"g-{max(numbers) + 1 if numbers else 1}"

    def _place(self, x, y, column: int) -> Tuple[float, float]:
        if x is not None and y is not None:
            return x, y
        same = sum(1 for n in self.nodes.values() if round(n["xCoordinate"]) == column * self.COLUMN)
        return column * self.COLUMN, 100 + same * self.ROW

    def _add(self, name: str, param: str, settings: Dict, x, y, column: int) -> str:
        key = self._next_key()
        x, y = self._place(x, y, column)
        self.nodes[key] = {"nodeName": name, "xCoordinate": x, "yCoordinate": y, "param": param, "nodeSettings": settings}
        return key

    def process(self, process_id: Union[int, str]) -> Dict:
        key = str(process_id)
        if key not in self._processes:
            self._processes[key] = self._get_process(int(process_id))
        return self._processes[key]

    def add_process(self, process_id: Union[int, str], x: Optional[float] = None, y: Optional[float] = None, name: Optional[str] = None) -> str:
        """Add a process node and return its key (g-N)."""
        process = self.process(process_id)
        return self._add(name or process.get("name") or str(process_id), str(process_id), {}, x, y, column=1)

    def pipeline(self, pipeline_id: Union[int, str]) -> Dict:
        """A module pipeline as get_pipeline returns it, read once."""
        number = int(pipeline_id)
        if number not in self._pipelines:
            if self._get_pipeline is None:
                raise PipelineGraphError("This builder has no get_pipeline to read module pipelines with; use Pipelines.builder().")
            pipeline = self._get_pipeline(number)
            if not isinstance(pipeline, dict) or not pipeline.get("id"):
                raise PipelineGraphError(f"Pipeline {number} could not be read as a module.")
            self._pipelines[number] = pipeline
        return self._pipelines[number]

    def _inner_parameter(self, port: Dict, kind: str) -> Dict:
        """The inner process parameter behind a module port: by slot on a process end,
        by parameter id on the end of a module nested inside it."""
        params = self.process(port["process_id"])[kind]
        slot = port["process_slot"]
        if port["side"] in ("i", "o") and 0 <= slot < len(params) \
                and str(params[slot].get("parameter_id")) == str(port["parameter_id"]):
            return params[slot]
        return next((p for p in params if str(p.get("parameter_id")) == str(port["parameter_id"])), {})

    def module_ports(self, pipeline_id: Union[int, str]) -> Dict[str, List[Dict]]:
        """A pipeline's ports as a module: {"inputs": [...], "outputs": [...]}.

        Each port is {slot, name, process_id, parameter_id, file_type, qualifier}:
        slot its 0-based order, name the module pipeline's own input or output
        node, and the rest the inner process parameter that consumes or produces it.
        """
        number = int(pipeline_id)
        if number not in self._module_ports:
            module = self.pipeline(number)
            nodes = parse_nodes(module.get("nodes"))
            ports = {}
            for kind, found in _module_io_ports(number, module.get("edges") or []).items():
                ports[kind] = []
                for slot, port in enumerate(found):
                    parameter = self._inner_parameter(port, kind)
                    ports[kind].append({
                        "slot": slot,
                        "name": nodes.get(port["node"], {}).get("nodeName"),
                        "process_id": port["process_id"],
                        "parameter_id": port["parameter_id"],
                        "file_type": parameter.get("file_type") or parameter.get("fileType") or "",
                        "qualifier": parameter.get("qualifier") or "",
                    })
            self._module_ports[number] = ports
        return self._module_ports[number]

    def _check_nesting(self, pipeline_id: int, chain: Tuple[int, ...] = ()) -> None:
        """Refuse a module that holds the pipeline being built, holds itself, or nests too deep."""
        path = " > ".join(map(str, chain + (pipeline_id,)))
        if pipeline_id in self._own_ids:
            raise PipelineGraphError(
                f"A pipeline cannot hold itself as a module: {path} reaches pipeline {pipeline_id}, "
                "the pipeline being built or a revision of it."
            )
        if pipeline_id in chain:
            raise PipelineGraphError(f"Module pipeline {chain[0]} holds itself: {path}.")
        if len(chain) >= MAX_MODULE_DEPTH:
            raise PipelineGraphError(f"Modules nest at most {MAX_MODULE_DEPTH} deep; {path} is deeper.")
        for node in parse_nodes(self.pipeline(pipeline_id).get("nodes")).values():
            inner = module_id(node.get("param"))
            if inner is not None:
                self._check_nesting(inner, chain + (pipeline_id,))

    def add_module(self, pipeline_id: Union[int, str], x: Optional[float] = None, y: Optional[float] = None, name: Optional[str] = None) -> str:
        """Add another pipeline as a module node and return its node key (g-N).

        Reads the module pipeline and every module inside it, and refuses one that
        holds the pipeline being built or nests more than MAX_MODULE_DEPTH deep.
        """
        pipeline_id = int(pipeline_id)
        self._check_nesting(pipeline_id)
        self.module_ports(pipeline_id)
        module = self.pipeline(pipeline_id)
        return self._add(name or module.get("name") or f"p{pipeline_id}", f"p{pipeline_id}", {}, x, y, column=1)

    def add_input(self, name: str, x: Optional[float] = None, y: Optional[float] = None) -> str:
        """Add a pipeline input. Its name is the field label on the run page."""
        return self._add(name, INPUT_NODE, {}, x, y, column=0)

    def add_output(self, name: str, publish: Optional[str] = None, x: Optional[float] = None, y: Optional[float] = None) -> str:
        """Add a pipeline output. ``publish`` (html, rdata, ...) shows it as a report of that type."""
        settings = {"pubWeb": publish} if publish else {}
        return self._add(name, OUTPUT_NODE, settings, x, y, column=2)

    def _node(self, key: str) -> Dict:
        if key not in self.nodes:
            raise PipelineGraphError(f"No node {key} in this pipeline.")
        return self.nodes[key]

    @staticmethod
    def _slot(params: List[Dict], which: Union[None, int, str], node: str, kind: str) -> Tuple[int, Dict]:
        """Find a process input or output by slot index, sname, name or parameter id."""
        if which is None:
            if len(params) != 1:
                raise PipelineGraphError(f"{node} has {len(params)} {kind}s; name the one to connect.")
            return 0, params[0]
        if isinstance(which, int) and 0 <= which < len(params):
            return which, params[which]
        matches = [
            (i, p) for i, p in enumerate(params)
            if str(which) in (p.get("sname"), p.get("name"), str(p.get("parameter_id")))
        ]
        if len(matches) != 1:
            found = "no" if not matches else "more than one"
            raise PipelineGraphError(f"{node} has {found} {kind} matching {which!r}.")
        return matches[0]

    def _ports(self, node: Dict, kind: str) -> List[Dict]:
        """A process node's inputs or outputs, or a module node's ports."""
        inner = module_id(node["param"])
        if inner is not None:
            return self.module_ports(inner)[kind]
        return self.process(node["param"])[kind]

    def _end(self, node_key: str, kind: str, which: Union[None, int, str]) -> Tuple[str, Dict]:
        """(edge end, parameter) for the chosen input or output of a process or module node."""
        node = self._node(node_key)
        slot, parameter = self._slot(self._ports(node, kind), which, node_key, kind[:-1])
        side, number = ("i" if kind == "inputs" else "o"), node_key.split("-")[1]
        if module_id(node["param"]) is not None:
            return f"p{side}-{parameter['process_id']}-{slot}-{parameter['parameter_id']}-{number}", parameter
        return f"{side}-{node['param']}-{slot}-{parameter['parameter_id']}-{number}", parameter

    def _connected_inputs(self, input_key: str) -> List[Dict]:
        targets = []
        for edge in self.edges:
            source, target = parse_edge(edge)
            if source["node"] == input_key:
                targets.append(self._ports(self._node(target["node"]), "inputs")[target["slot"]])
        return targets

    def connect(self, source: str, target: str, output: Union[None, int, str] = None, input: Union[None, int, str] = None) -> str:
        """Connect source (a process, module or pipeline input) to target (a process, module or pipeline output).

        ``output`` and ``input`` pick the process's slot by index, sname, name or
        parameter id, or the module's port by index or name; leave one out when
        there is a single choice. Raises PipelineGraphError when the types do not match.
        """
        src, dst = self._node(source), self._node(target)
        src_n, dst_n = source.split("-")[1], target.split("-")[1]
        if src["param"] == OUTPUT_NODE or dst["param"] == INPUT_NODE:
            raise PipelineGraphError("Edges run from a process or pipeline input to a process or pipeline output.")
        if src["param"] == INPUT_NODE and dst["param"] == OUTPUT_NODE:
            raise PipelineGraphError("A pipeline input cannot feed a pipeline output directly.")

        if dst["param"] == OUTPUT_NODE:
            out_end, out = self._end(source, "outputs", output)
            edge = f"i-{OUTPUT_NODE}-1-{out['parameter_id']}-{dst_n}_{out_end}"
        else:
            in_end, inp = self._end(target, "inputs", input)
            if src["param"] == INPUT_NODE:
                for other in self._connected_inputs(source):
                    if not compatible(other, inp):
                        raise PipelineGraphError(
                            f"{source} already feeds a {_type_of(other)} input; {target} wants {_type_of(inp)}."
                        )
                earlier = [parse_edge(e)[0] for e in self.edges if parse_edge(e)[0]["node"] == source]
                parameter_id = earlier[0]["parameterId"] if earlier else inp["parameter_id"]
                edge = f"o-{INPUT_NODE}-1-{parameter_id}-{src_n}_{in_end}"
            else:
                out_end, out = self._end(source, "outputs", output)
                if not compatible(out, inp):
                    raise PipelineGraphError(
                        f"{source} output {out.get('name')} is {_type_of(out)}; "
                        f"{target} input {inp.get('name')} wants {_type_of(inp)}."
                    )
                edge = f"{out_end}_{in_end}"

        if edge in self.edges:
            return edge
        target_handle = parse_edge(edge)[1]
        if dst["param"] != OUTPUT_NODE and any(parse_edge(e)[1] == target_handle for e in self.edges):
            raise PipelineGraphError(f"{target} input slot {target_handle['slot']} is already connected.")
        self.edges.append(edge)
        return edge

    def graph(self) -> Dict:
        return {"nodes": self.nodes, "edges": self.edges}


class Pipelines:
    """Read, create and save pipelines through the editor's own endpoint."""

    def __init__(self, client) -> None:
        self.client = client

    def get_pipeline(self, pipeline_id: int) -> Dict:
        """One pipeline's fields, with nodes, edges and mainG parsed into the saved shape."""
        response = self.client.call("GET", f"/api/pipeline/v1/{pipeline_id}/details")
        wrapped = (response or {}).get("pipeline", response) or {}
        pipeline = dict(wrapped.get(f"main_pipeline_{pipeline_id}", wrapped))
        pipeline["nodes"] = parse_nodes(pipeline.get("nodes"))
        pipeline["edges"] = _json_field(pipeline.get("edges"), "edges") or []
        pipeline["mainG"] = _json_field(pipeline.get("mainG"), "mainG") or [0, 0, 1]
        pipeline["updateAllowed"] = (response or {}).get("updateAllowed")
        return pipeline

    def create_pipeline(
        self,
        name: str,
        pipeline_group_id: int,
        nodes: Optional[Dict] = None,
        edges: Optional[List[str]] = None,
        summary: str = "",
        description: str = "",
        permission: int = 3,
        script_pipe_config: str = DEFAULT_PIPE_CONFIG,
        main_g: Optional[List[float]] = None,
        **fields,
    ) -> Dict:
        """Create a pipeline, private (permission 3) unless told otherwise.

        ``pipeline_group_id`` is a pipeline menu group, not a process menu group.
        Extra camelCase save fields (scriptPipeHeader, publishWebDir, ...) pass through.
        """
        body = {
            "name": name,
            "summary": summary,
            "description": description,
            "pipelineGroupId": pipeline_group_id,
            "pipelineType": "ViaFoundry",
            "version": "1.0.0",
            "revComment": "Initial Version",
            "permission": permission,
            "pin": "false",
            "publiclySearchable": "false",
            "nodes": nodes or {},
            "edges": edges or [],
            "mainG": main_g or [0, 0, 0.7],
            "scriptPipeConfig": script_pipe_config,
            "scriptPipeHeader": "",
            "scriptPipeFooter": "",
            "scriptModeHeader": "groovy",
            "scriptModeFooter": "groovy",
            "publishWebDir": "",
            "publishWebAppDir": "",
            "publishDMetaDir": "",
            **fields,
        }
        return self.client.call("POST", "/api/pipeline/v1", data=body)

    @staticmethod
    def save_body(pipeline: Dict) -> Dict:
        """The save request for a pipeline read with get_pipeline."""
        body = {saved: pipeline.get(read) for saved, read in _SAVE_FIELDS.items() if read in pipeline}
        body.update(id=pipeline["id"], nodes=pipeline["nodes"], edges=pipeline["edges"], mainG=pipeline["mainG"])
        return body

    def update_pipeline(self, pipeline_id: int, **changes) -> Dict:
        """Save over a pipeline, changing only the camelCase fields given (nodes, edges, name, ...).

        Reads the pipeline first and resends every other field as it is, because
        the save replaces the whole pipeline. The save edits in place (same id,
        same revision), so runs already made from it see the change; save only
        over a pipeline you own and that no one else runs.
        """
        body = self.save_body(self.get_pipeline(pipeline_id))
        unknown = set(changes) - set(body) - {"nodes", "edges", "mainG"}
        if unknown:
            raise ValueError(f"Not a pipeline save field: {', '.join(sorted(unknown))}")
        body.update(changes)
        return self.client.call("POST", "/api/pipeline/v1", data=body)

    def builder(self, pipeline_id: Optional[int] = None) -> PipelineBuilder:
        """A builder that reads processes and module pipelines from the server, optionally
        starting from a saved pipeline (which it then refuses to take as its own module)."""
        def get_process(process_id: int) -> Dict:
            return self.client.call("GET", f"/api/v1/process/{process_id}")

        if pipeline_id is None:
            return PipelineBuilder(get_process, get_pipeline=self.get_pipeline)
        pipeline = self.get_pipeline(pipeline_id)
        return PipelineBuilder(get_process, pipeline["nodes"], pipeline["edges"],
                               get_pipeline=self.get_pipeline, pipeline_id=pipeline_id)
