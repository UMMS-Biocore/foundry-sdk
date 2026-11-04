# Changelog

## 1.4.0

### Added
- **Pipelines as modules**
  - `PipelineBuilder.add_module(pipeline_id, x=None, y=None, name=None)` adds
    another pipeline as a module node (param `p<pipeline id>`), named after
    that pipeline unless `name` is given.
  - `PipelineBuilder.module_ports(pipeline_id)` returns a pipeline's ports as a
    module, `{"inputs": [...], "outputs": [...]}`, each with its `slot`,
    `name`, `process_id`, `parameter_id`, `file_type` and `qualifier`. Ports
    are numbered as the server numbers them.
  - `connect` accepts a module at either end. `output` and `input` pick a
    module port by 0-based slot or name, with the same file type check as a
    process, and the edge ends are written `pi-` and `po-` as the editor
    writes them.
  - The builder takes `get_pipeline` to read module pipelines, and
    `pipeline_id` and `revision_ids` for the pipeline being built.
    `Pipelines.builder()` sets them. A module that holds the pipeline being
    built, holds itself, or nests more than five deep is refused.

### Changed
- `parse_edge` returns module edge ends (`pi`, `po`) in dataflow order,
  whichever end is written first.
