"""Create, configure and launch pipeline runs."""
import re
from typing import Dict, List, Optional

_SAFE_SEGMENT = re.compile(r"[^A-Za-z0-9._-]")
# A login never starts with a dot, so "." and ".." cannot climb out of /home.
_LOGIN_NAME = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._-]*")


def default_execution_directory(environment: Dict, run_name: str) -> Optional[str]:
    """Proposed execution directory for a new run, or None when the user must choose.

    The environment's declared default wins, as in the web interface; otherwise
    /home/<login>/foundry-connect-runs/<run name>, where <login> is the run
    environment's own login name.
    """
    declared = (environment.get("defWorkdir") or "").strip()
    if declared:
        return declared
    login = (environment.get("username") or "").strip()
    if not _LOGIN_NAME.fullmatch(login):
        return None
    segment = _SAFE_SEGMENT.sub("_", (run_name or "").strip()).lstrip(".") or "run"
    return f"/home/{login}/foundry-connect-runs/{segment}"


class Runs:
    """Start a run from a pipeline: project, pipeline, run, form, save, launch."""

    def __init__(self, client) -> None:
        self.client = client

    def list_projects(self, name: Optional[str] = None, limit: int = 20) -> Dict:
        params = {"type": "1", "take": limit}
        if name:
            params["name"] = name
        return self.client.call("GET", "/api/v1/project/", params=params)

    def create_project(self, name: str, summary: str = "") -> Dict:
        data = {"name": name}
        if summary:
            data["summary"] = summary
        return self.client.call("POST", "/api/v1/project/", data=data)

    def list_pipelines(self, search: Optional[str] = None, limit: int = 20) -> Dict:
        params = {"type": "1,2,3,4", "take": limit}
        if search:
            params["searchKeyword"] = search
        return self.client.call("GET", "/api/v1/pipeline/", params=params)

    def create_run(self, pipeline_id: int, project_id: int, name: str) -> int:
        """Create an unlaunched run and return its id."""
        created = self.client.call(
            "POST",
            "/api/v1/run/new-run-attempt",
            data={"pipelineId": pipeline_id, "projectId": project_id, "name": name},
        )
        run_id = (created or {}).get("id") or (created or {}).get("projectPipelineId")
        if not run_id:
            raise RuntimeError(f"The server did not return the new run's id: {created}")
        return run_id

    def get_run_form(self, run_id: int) -> Dict:
        """Inputs, process options and runEnvironment.availableList for a run."""
        return self.client.call("GET", f"/api/v1/run/{run_id}/details")

    def save_run(
        self,
        run_id: int,
        permission: int,
        inputs: Optional[List[Dict]] = None,
        process_options: Optional[Dict] = None,
        group_id: Optional[int] = None,
        run_environment_id: Optional[int] = None,
        launch_directory: Optional[str] = None,
        publish_dir: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Dict:
        """Save only the fields given.

        On a Foundry pipeline, inputs merge with the saved ones; on an external
        (nf-core) pipeline the inputs dict is replaced whole, so send it complete.
        process_options always replaces the whole set.
        """
        fields = {
            "inputs": inputs,
            "processOptions": process_options,
            "groupId": group_id,
            "runEnvironmentId": run_environment_id,
            "launchDirectory": launch_directory,
            "publishDir": publish_dir,
            "name": name,
        }
        data = {"permission": permission, **{k: v for k, v in fields.items() if v is not None}}
        return self.client.call("PATCH", f"/api/v1/run/{run_id}/save", data=data)

    def launch_run(self, run_id: int, run_type: str = "newrun") -> Dict:
        return self.client.call("POST", "/api/v1/run/initiate-run", data={"runId": run_id, "runType": run_type})

    def run_status(self, run_id: int) -> Dict:
        return self.client.call("GET", f"/api/v1/run/{run_id}/status")
