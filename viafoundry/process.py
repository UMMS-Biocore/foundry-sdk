class Process:
    """
    A class for managing processes in the ViaFoundry API.

    FIXME: Circular dependency with ViaFoundryClient, using a string here - but need to refactor
    FIXME: Raise specific errors for better handling

    Attributes:
        client (ViaFoundryClient): The client instance to interact with the API.
    """

    def __init__(self, client) -> None:
        """
        Initializes the Process class.

        Args:
            client (ViaFoundryClient): The client instance to interact with.
        """
        self.client = client

    def list_processes(self) -> dict:
        """
        Lists all existing processes.

        Returns:
            dict: A dictionary of existing processes.

        Raises:
            Exception: If listing processes fails.

        FIXME:
            Subclass and raise a more specific exception
        """
        try:
            endpoint = "/api/v1/process/"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception("Error 1001: Failed to list processes") from e

    def get_process(self, process_id: str) -> dict:
        """
        Retrieves information about a specific process.

        Args:
            process_id (str): The ID of the process to retrieve.

        Returns:
            dict: The process information.

        Raises:
            Exception: If retrieving the process fails.
        """
        try:
            endpoint = f"/api/v1/process/{process_id}"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception(
                f"Error 1002: Failed to retrieve process with ID {process_id}"
            ) from e

    def get_process_revisions(self, process_id: str) -> dict:
        """
        Gets all revisions for the given process.

        Args:
            process_id (str): The ID of the process to get revisions for.

        Returns:
            dict: A dictionary of revisions for the process.

        Raises:
            Exception: If retrieving revisions fails.
        """
        try:
            endpoint = f"/api/v1/process/{process_id}/revisions"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception(
                f"Error 1003: Failed to get revisions for process ID {process_id}"
            ) from e

    def check_process_usage(self, process_id: str) -> dict:
        """
        Checks if a process is used in pipelines or runs.

        Args:
            process_id (str): The ID of the process to check.

        Returns:
            dict: Information about the process usage.

        Raises:
            Exception: If checking usage fails.
        """
        try:
            endpoint = f"/api/v1/process/{process_id}/is-used"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception(
                f"Error 1004: Failed to check usage for process ID {process_id}"
            ) from e

    def duplicate_process(self, process_id: str) -> dict:
        """
        Duplicates a process.

        Args:
            process_id (str): The ID of the process to duplicate.

        Returns:
            dict: Information about the duplicated process.

        Raises:
            Exception: If duplicating the process fails.
        """
        try:
            endpoint = f"/api/v1/process/{process_id}/duplicate"
            return self.client.call("POST", endpoint)
        except Exception as e:
            raise Exception(
                f"Error 1005: Failed to duplicate process with ID {process_id}"
            ) from e

    def create_menu_group(self, name: str) -> dict:
        """
        Creates a new menu group.

        Args:
            name (str): The name of the menu group to create.

        Returns:
            dict: Information about the created menu group.

        Raises:
            Exception: If creating the menu group fails.
        """
        try:
            payload = {"name": name}
            endpoint = f"/api/v1/menu-group/process"
            return self.client.call("POST", endpoint, data=payload)
        except Exception as e:
            raise Exception(
                f"Error 1006: Failed to create menu group with name '{name}'"
            ) from e

    def list_menu_groups(self) -> dict:
        """
        Lists all menu groups.

        Returns:
            dict: A dictionary of menu groups.

        Raises:
            Exception: If listing menu groups fails.
        """
        try:
            endpoint = "/api/v1/menu-group/process"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception("Error 1007: Failed to list menu groups") from e

    def update_menu_group(self, menu_group_id: str, name: str) -> dict:
        """
        Updates a menu group.

        Args:
            menu_group_id (str): The ID of the menu group to update.
            name (str): The new name for the menu group.

        Returns:
            dict: Information about the updated menu group.

        Raises:
            Exception: If updating the menu group fails.
        """
        try:
            payload = {"name": name}
            endpoint = f"/api/v1/menu-group/process/{menu_group_id}"
            return self.client.call("POST", endpoint, data=payload)
        except Exception as e:
            raise Exception(
                f"Error 1008: Failed to update menu group with ID {menu_group_id}"
            ) from e

    def create_process(self, process_data: dict) -> dict:
        """
        Creates a new process.

        Args:
            process_data (dict): The data for the new process.

        Returns:
            dict: Information about the created process.

        Raises:
            Exception: If creating the process fails.
        """
        try:
            endpoint = "/api/v1/process"
            return self.client.call("POST", endpoint, data=process_data)
        except Exception as e:
            raise Exception("Error 1009: Failed to create a new process") from e

    def update_process(self, process_id: str, process_data: dict) -> dict:
        """
        Updates an existing process.

        Args:
            process_id (str): The ID of the process to update.
            process_data (dict): The updated data for the process.

        Returns:
            dict: Information about the updated process.

        Raises:
            Exception: If updating the process fails.
        """
        try:
            endpoint = f"/api/v1/process/{process_id}"
            return self.client.call("PUT", endpoint, data=process_data)
        except Exception as e:
            raise Exception(
                f"Error 1010: Failed to update process with ID {process_id}"
            ) from e

    def delete_process(self, process_id: str) -> None:
        """
        Deletes a process.

        Args:
            process_id (str): The ID of the process to delete.

        Raises:
            Exception: If deleting the process fails.
        """
        try:
            endpoint = f"/api/v1/process/{process_id}"
            return self.client.call("DELETE", endpoint)
        except Exception as e:
            raise Exception(
                f"Error 1011: Failed to delete process with ID {process_id}"
            ) from e

    def get_pipeline_parameters(self, pipeline_id: str) -> dict:
        """
        Gets parameter list for a pipeline.

        Args:
            pipeline_id (str): The ID of the pipeline to retrieve parameters for.

        Returns:
            dict: A dictionary of parameters for the pipeline.

        Raises:
            Exception: If retrieving parameters fails.
        """
        try:
            endpoint = f"/api/run/v1/pipeline/{pipeline_id}/parameter-list"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception(
                f"Error 1012: Failed to get parameters for pipeline ID {pipeline_id}"
            ) from e

    def list_parameters(self) -> dict:
        """
        Lists all parameters.

        Returns:
            dict: A dictionary of parameters.

        Raises:
            Exception: If listing parameters fails.
        """
        try:
            endpoint = f"/api/parameter/v1"
            return self.client.call("GET", endpoint)
        except Exception as e:
            raise Exception("Error 1013: Failed to list parameters") from e

    def create_parameter(self, parameter_data: dict) -> dict:
        """
        Creates a new parameter.

        Args:
            parameter_data (dict): The data for the new parameter.

        Returns:
            dict: Information about the created parameter.

        Raises:
            Exception: If creating the parameter fails.
        """
        try:
            endpoint = "/api/parameter/v1"
            return self.client.call("POST", endpoint, data=parameter_data)
        except Exception as e:
            raise Exception("Error 1014: Failed to create a new parameter") from e

    def update_parameter(self, parameter_id: str, parameter_data: dict) -> dict:
        """
        Updates an existing parameter.

        Args:
            parameter_id (str): The ID of the parameter to update.
            parameter_data (dict): The updated data for the parameter.

        Returns:
            dict: Information about the updated parameter.

        Raises:
            Exception: If updating the parameter fails.
        """
        try:
            endpoint = f"/api/parameter/v1/{parameter_id}"
            return self.client.call("POST", endpoint, data=parameter_data)
        except Exception as e:
            raise Exception(
                f"Error 1015: Failed to update parameter with ID {parameter_id}"
            ) from e

    def delete_parameter(self, parameter_id: str) -> None:
        """
        Deletes an existing parameter.

        Args:
            parameter_id (str): The ID of the parameter to delete.

        Raises:
            Exception: If deleting the parameter fails.
        """
        try:
            endpoint = f"/api/parameter/v1/{parameter_id}"
            return self.client.call("DELETE", endpoint)
        except Exception as e:
            raise Exception(
                f"Error 1016: Failed to delete parameter with ID {parameter_id}"
            ) from e

    def get_menu_group_by_name(self, group_name: str) -> str | None:
        """
        Finds a menu group by its name.

        Args:
            group_name (str): The name of the menu group to find.

        Returns:
            str | None: The ID of the menu group if found, otherwise None.

        Raises:
            Exception: If listing menu groups fails.
        """
        try:
            menu_groups = self.list_menu_groups()
            for group in menu_groups.get("data", []):
                if group.get('name', '').lower() == group_name.lower():
                    return group.get('id')
            return None
        except Exception as e:
            print(f"Error finding menu group: {str(e)}")
            return None

    def filter_parameters(
        self,
        name: str = None,
        qualifier: str = None,
        fileType: str = None,
        id_: str = None
    ) -> list:
        """
        Filters parameters by optional name, qualifier, fileType, and id.
        All filters are case-insensitive and optional.

        Args:
            name (str, optional): Name to filter by.
            qualifier (str, optional): Qualifier to filter by.
            fileType (str, optional): File type to filter by.
            id_ (str, optional): ID to filter by.

        Returns:
            list: List of filtered parameter dictionaries.

        Raises:
            Exception: If listing parameters fails.
        """
        try:
            all_params = self.list_parameters()
            params = all_params.get("data", []) if isinstance(all_params, dict) else all_params
            filtered = []
            for param in params:
                if name and name.lower() not in param.get('name', '').lower():
                    continue
                if qualifier and qualifier.lower() != param.get('qualifier', '').lower():
                    continue
                if fileType and fileType.lower() != param.get('fileType', '').lower():
                    continue
                if id_ and id_ != str(param.get('id', '')):
                    continue
                filtered.append(param)
            # Print results
            for param in filtered:
                print(
                    f"ID: {param.get('id')}, Name: {param.get('name')}, "
                    f"Qualifier: {param.get('qualifier', '')}, FileType: {param.get('fileType', '')}"
                )
            return filtered
        except Exception as e:
            print(f"Error filtering parameters: {str(e)}")
            return []

    def create_process_config(
        self,
        name: str,
        menu_group_name: str,
        input_params: list,
        output_params: list,
        summary: str = "",
        script_body: str = "",
        script_language: str = "bash",
        script_header: str = "",
        script_footer: str = "",
        permission_settings: dict = None,
        revision_comment: str = "Initial revision"
    ) -> dict:
        """
        Creates a full process configuration with all required fields.

        Args:
            name (str): Name of the process.
            menu_group_name (str): Name of the menu group.
            input_params (list): List of input parameter dicts.
            output_params (list): List of output parameter dicts.
            summary (str, optional): Summary of the process.
            script_body (str, optional): Script body.
            script_language (str, optional): Script language.
            script_header (str, optional): Script header.
            script_footer (str, optional): Script footer.
            permission_settings (dict, optional): Permission settings.
            revision_comment (str, optional): Revision comment.

        Returns:
            dict: The process configuration dictionary.

        Raises:
            ValueError: If the menu group is not found.
        """
        menu_group_id = self.get_menu_group_by_name(menu_group_name)
        if not menu_group_id:
            raise ValueError(f"Menu group '{menu_group_name}' not found")

        if permission_settings is None:
            permission_settings = {
                "viewPermissions": 3,
                "writeGroupIds": []
            }

        process_config = {
            "name": name,
            "menuGroupId": menu_group_id,
            "summary": summary,
            "inputParameters": [],
            "outputParameters": [],
            "script": {
                "body": script_body,
                "header": script_header,
                "footer": script_footer,
                "language": script_language
            },
            "permissionSettings": permission_settings,
            "revisionComment": revision_comment
        }

        # Add input parameters
        for param in input_params:
            matched_params = self.filter_parameters(
                name=param.get('name'),
                qualifier=param.get('qualifier'),
                fileType=param.get('fileType'),
                id_=param.get('id')
            )
            if matched_params:
                p = matched_params[0]
                process_config['inputParameters'].append({
                    "parameterId": p['id'],
                    "displayName": param.get('displayName', p.get('name', '')),
                    "operator": param.get('operator', ""),
                    "operatorContent": param.get('operatorContent', ""),
                    "optional": param.get('optional', False),
                    "test": param.get('test', "")
                })

        # Add output parameters
        for param in output_params:
            matched_params = self.filter_parameters(
                qualifier=param.get('qualifier'),
                fileType=param.get('fileType'),
                id_=param.get('id')
            )
            if matched_params:
                p = matched_params[0]
                process_config['outputParameters'].append({
                    "parameterId": p['id'],
                    "displayName": param.get('displayName', p.get('name', '')),
                    "operator": param.get('operator', ""),
                    "operatorContent": param.get('operatorContent', ""),
                    "optional": param.get('optional', False)
                })

        return process_config
