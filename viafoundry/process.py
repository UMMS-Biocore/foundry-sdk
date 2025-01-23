class Process:
    def __init__(self, client):
        self.client = client

    def list_processes(self):
        """List all existing processes."""
        try:
            endpoint = f"/api/v1/process/"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception("Error 1001: Failed to list processes") from e

    def get_process(self, process_id):
        """Retrieve information about a specific process."""
        try:
            endpoint = f"/api/v1/process/{process_id}"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception(f"Error 1002: Failed to retrieve process with ID {process_id}") from e

    def get_process_revisions(self, process_id):
        """Get all revisions for the given process."""
        try:
            endpoint = f"/api/v1/process/{process_id}/revisions"
            return self.client.call("GET", endpoint) 
        except Exception as e:
            raise Exception(f"Error 1003: Failed to get revisions for process ID {process_id}") from e

    def check_process_usage(self, process_id):
        """Check if a process is used in pipelines or runs."""
        try:
            endpoint = f"/api/v1/process/{process_id}/is-used"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception(f"Error 1004: Failed to check usage for process ID {process_id}") from e

    def duplicate_process(self, process_id):
        """Duplicate a process."""
        try:
            endpoint = f"/api/v1/process/{process_id}/duplicate"
            return self.client.call("POST", endpoint)
        except Exception as e:
            raise Exception(f"Error 1005: Failed to duplicate process with ID {process_id}") from e

    def create_menu_group(self, name):
        """Create a new menu group."""
        try:
            payload = {"name": name}
            endpoint = f"/api/v1/menu-group/process"
            return self.client.call("POST", endpoint, data=payload)
        except Exception as e:
            raise Exception(f"Error 1006: Failed to create menu group with name '{name}'") from e

    def list_menu_groups(self):
        """List all menu groups."""
        try:
            endpoint = f"/api/v1/menu-group/process"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception("Error 1007: Failed to list menu groups") from e

    def update_menu_group(self, menu_group_id, name):
        """Update a menu group."""
        try:
            payload = {"name": name}
            endpoint =  f"/api/v1/menu-group/process/{menu_group_id}"
            return self.client.call("POST", endpoint, data=payload)
        except Exception as e:
            raise Exception(f"Error 1008: Failed to update menu group with ID {menu_group_id}") from e

    def create_process(self, process_data):
        """Create a new process."""
        try:
            endpoint =  f"/api/v1/process"
            return self.client.call("POST", endpoint, data=process_data)
        except Exception as e:
            raise Exception("Error 1009: Failed to create a new process") from e

    def update_process(self, process_id, process_data):
        """Update an existing process."""
        try:
            endpoint = f"/api/v1/process/{process_id}"
            return self.client.call("PUT", endpoint, data=process_data)
        except Exception as e:
            raise Exception(f"Error 1010: Failed to update process with ID {process_id}") from e

    def delete_process(self, process_id):
        """Delete a process."""
        try:
            endpoint = f"/api/v1/process/{process_id}"
            return self.client.call("DELETE", endpoint)
        except Exception as e:
            raise Exception(f"Error 1011: Failed to delete process with ID {process_id}") from e

    def get_pipeline_parameters(self, pipeline_id):
        """Get parameter list for a pipeline."""
        try:
            endpoint = f"/api/run/v1/pipeline/{pipeline_id}/parameter-list"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception(f"Error 1012: Failed to get parameters for pipeline ID {pipeline_id}") from e

    def list_parameters(self):
        """List all parameters."""
        try:
            endpoint = f"/api/parameter/v1"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception("Error 1013: Failed to list parameters") from e

    def create_parameter(self, parameter_data):
        """Create a new parameter."""
        try:
            endpoint = "/api/parameter/v1"
            return self.client.call("POST", endpoint, data=parameter_data)
        except Exception as e:
            raise Exception("Error 1014: Failed to create a new parameter") from e

    def update_parameter(self, parameter_id, parameter_data):
        """Update an existing parameter."""
        try:
            endpoint = f"/api/parameter/v1/{parameter_id}"
            return self.client.call("POST", endpoint, data=parameter_data)
        except Exception as e:
            raise Exception(f"Error 1015: Failed to update parameter with ID {parameter_id}") from e

    def delete_parameter(self, parameter_id):
        """Delete an existing parameter."""
        try:
            endpoint = f"/api/parameter/v1/{parameter_id}"
            return self.client.call("DELETE", endpoint)
        except Exception as e:
            raise Exception(f"Error 1016: Failed to delete parameter with ID {parameter_id}") from e