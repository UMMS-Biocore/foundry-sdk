from copy import deepcopy

class Metadata:
    """
    A class for managing metadata in the ViaFoundry API.

    Attributes:
        client (ViaFoundryClient): The client instance to interact with the API.
    """

    def __init__(self, client) -> None:
        """
        Initializes the Metadata class.

        Args:
            client (ViaFoundryClient): The client instance to interact with.
        """
        self.client = client

    # --- Project Methods ---
    def search_projects(self, search_params: dict = None) -> dict:
        """
        Searches for projects using the metadata API.

        Args:
            search_params (dict, optional): Search parameters for the project search. Defaults to None.

        Returns:
            dict: The search results for projects.

        Raises:
            Exception: If the search fails.
        """
        try:
            endpoint = "/api/v1/vmeta/project/search"
            data = search_params if search_params is not None else {}
            return self.client.call("POST", endpoint, data=data)
        except Exception as e:
            raise Exception(f"Error 2001: Failed to search projects: {e}") from e

    def create_project(self, project_data: dict) -> dict:
        """
        Creates a new metadata project.

        Args:
            project_data (dict): Data required to create the project.

        Returns:
            dict: The created project.

        Raises:
            Exception: If the creation fails.
        """
        try:
            return self.client.call("POST", "/api/v1/vmeta/project/create", data=project_data)
        except Exception as e:
            raise Exception(f"Error 2002: Failed to create project: {e}") from e

    def get_project(self, project_id: str) -> dict:
        """
        Retrieves a project by its ID.

        Args:
            project_id (str): The ID of the project.

        Returns:
            dict: The project details.

        Raises:
            Exception: If retrieval fails.
        """
        try:
            return self.client.call("GET", f"/api/v1/vmeta/project/{project_id}")
        except Exception as e:
            raise Exception(f"Error 2003: Failed to get project {project_id}: {e}") from e

    def update_project(self, project_id: str, update_data: dict) -> dict:
        """
        Updates an existing project.

        Args:
            project_id (str): The ID of the project to update.
            update_data (dict): The data to update in the project.

        Returns:
            dict: The updated project.

        Raises:
            Exception: If update fails.
        """
        try:
            return self.client.call("PATCH", f"/api/v1/vmeta/project/{project_id}", data=update_data)
        except Exception as e:
            raise Exception(f"Error 2004: Failed to update project {project_id}: {e}") from e

    def delete_project(self, project_id: str) -> dict:
        """
        Deletes a project by its ID.

        Args:
            project_id (str): The ID of the project to delete.

        Returns:
            dict: The deletion result.

        Raises:
            Exception: If deletion fails.
        """
        try:
            return self.client.call("DELETE", f"/api/v1/vmeta/project/{project_id}")
        except Exception as e:
            raise Exception(f"Error 2005: Failed to delete project {project_id}: {e}") from e
    
    # --- Collection Methods ---
    def search_collections(self, search_params: dict = None) -> dict:
        """
        Searches for collections.

        Args:
            search_params (dict, optional): Collection search filters. Defaults to None.

        Returns:
            dict: The list of collections.

        Raises:
            Exception: If the search fails.
        """
        try:
            return self.client.call("POST", "/api/v1/vmeta/collection/search", data=search_params or {})
        except Exception as e:
            raise Exception(f"Error 2011: Failed to search collections: {e}") from e

    def create_collection(self, collection_data: dict) -> dict:
        """
        Creates a new collection.

        Args:
            collection_data (dict): The collection data.

        Returns:
            dict: The created collection.

        Raises:
            Exception: If creation fails.
        """
        try:
            return self.client.call("POST", "/api/v1/vmeta/collection/create", data=collection_data)
        except Exception as e:
            raise Exception(f"Error 2012: Failed to create collection: {e}") from e

    def get_collection(self, collection_id: str) -> dict:
        """
        Retrieves a collection by ID.

        Args:
            collection_id (str): The ID of the collection.

        Returns:
            dict: The collection details.

        Raises:
            Exception: If retrieval fails.
        """
        try:
            return self.client.call("GET", f"/api/v1/vmeta/collection/{collection_id}")
        except Exception as e:
            raise Exception(f"Error 2013: Failed to get collection {collection_id}: {e}") from e

    def update_collection(self, collection_id: str, update_data: dict) -> dict:
        """
        Updates a collection.

        Args:
            collection_id (str): The ID of the collection.
            update_data (dict): The data to update.

        Returns:
            dict: The updated collection.

        Raises:
            Exception: If update fails.
        """
        try:
            return self.client.call("PATCH", f"/api/v1/vmeta/collection/{collection_id}", data=update_data)
        except Exception as e:
            raise Exception(f"Error 2014: Failed to update collection {collection_id}: {e}") from e

    def delete_collection(self, collection_id: str) -> dict:
        """
        Deletes a collection.

        Args:
            collection_id (str): The ID of the collection.

        Returns:
            dict: Deletion confirmation.

        Raises:
            Exception: If deletion fails.
        """
        try:
            return self.client.call("DELETE", f"/api/v1/vmeta/collection/{collection_id}")
        except Exception as e:
            raise Exception(f"Error 2015: Failed to delete collection {collection_id}: {e}") from e
    
    # --- Field Methods ---
    def search_fields(self, search_params: dict = None) -> dict:
        """
        Searches for metadata fields.

        Args:
            search_params (dict, optional): Filters for the field search.

        Returns:
            dict: The list of fields.

        Raises:
            Exception: If the search fails.
        """
        try:
            return self.client.call("POST", "/api/v1/vmeta/field/search", data=search_params or {})
        except Exception as e:
            raise Exception(f"Error 2021: Failed to search fields: {e}") from e

    def create_field(self, field_data: dict) -> dict:
        """
        Creates a new metadata field.

        Args:
            field_data (dict): The data for the new field.

        Returns:
            dict: The created field.

        Raises:
            Exception: If creation fails.
        """
        try:
            return self.client.call("POST", "/api/v1/vmeta/field/create", data=field_data)
        except Exception as e:
            raise Exception(f"Error 2022: Failed to create field: {e}") from e

    def get_field(self, field_id: str) -> dict:
        """
        Retrieves a metadata field by ID.

        Args:
            field_id (str): ID of the field.

        Returns:
            dict: Field details.

        Raises:
            Exception: If retrieval fails.
        """
        try:
            return self.client.call("GET", f"/api/v1/vmeta/field/{field_id}")
        except Exception as e:
            raise Exception(f"Error 2023: Failed to get field {field_id}: {e}") from e

    def update_field(self, field_id: str, update_data: dict) -> dict:
        """
        Updates a metadata field.

        Args:
            field_id (str): ID of the field to update.
            update_data (dict): Updated field data.

        Returns:
            dict: Updated field.

        Raises:
            Exception: If update fails.
        """
        try:
            return self.client.call("PATCH", f"/api/v1/vmeta/field/{field_id}", data=update_data)
        except Exception as e:
            raise Exception(f"Error 2024: Failed to update field {field_id}: {e}") from e

    def delete_field(self, field_id: str) -> dict:
        """
        Deletes a metadata field.

        Args:
            field_id (str): ID of the field.

        Returns:
            dict: Deletion confirmation.

        Raises:
            Exception: If deletion fails.
        """
        try:
            return self.client.call("DELETE", f"/api/v1/vmeta/field/{field_id}")
        except Exception as e:
            raise Exception(f"Error 2025: Failed to delete field {field_id}: {e}") from e
    
    def get_collection_fields(self, collection_id: str) -> dict:
        """
        Retrieves a metadata field by collection_id.

        Args:
            collection_id (str): collectionID of the field.

        Returns:
            dict: Field details.

        Raises:
            Exception: If retrieval fails.
        """
        try:
            search_params = {
                "filter": {
                    "collectionID": collection_id
                }
            }
            return self.search_fields(search_params)
        except Exception as e:
            raise Exception(f"Error 2026: Failed to get fields for collection: {collection_id}: {e}") from e

    def get_project_fields(self, project_id: str) -> dict:
        """
        Retrieves all metadata fields for a given project by accumulating fields from all its collections.

        Args:
            project_id (str): projectID of the field.

        Returns:
            dict: All fields for the project, accumulated in a single dictionary with a "data" key containing a list.

        Raises:
            Exception: If retrieval fails.
        """
        try:
            search_params = {
                "filter": {
                    "projectID": project_id
                }
            }
            collections = self.search_collections(search_params)
            all_fields = []
            for collection in collections["data"]:
                fields = self.get_collection_fields(collection['_id'])
               
                # fields["data"] is expected to be a list of field dicts
                if "data" in fields and isinstance(fields["data"], list):
                    all_fields.extend(fields["data"])

            return {"data": all_fields}
        except Exception as e:
            raise Exception(f"Error 2027: Failed to get fields for project {project_id}: {e}") from e


    
    # --- Dataset Methods ---
    def search_dataset_files(self, dataset_id: str, filter_data: dict = None) -> dict:
        """
        Lists files associated with a dataset.

        Args:
            dataset_id (str): ID of the dataset.
            filter_data (dict, optional): Filter criteria.

        Returns:
            dict: Matching files.

        Raises:
            Exception: If listing fails.
        """
        try:
            return self.client.call("POST", f"/api/v1/vmeta/dataset/{dataset_id}/files/search", data=filter_data or {})
        except Exception as e:
            raise Exception(f"Error 2036: Failed to search dataset files for {dataset_id}: {e}") from e

    def add_files_to_dataset(self, dataset_id: str, file_data: dict) -> dict:
        """
        Adds files to a dataset.

        Args:
            dataset_id (str): ID of the dataset.
            file_data (dict): File metadata.

        Returns:
            dict: Confirmation of file addition.

        Raises:
            Exception: If operation fails.
        """
        try:
            return self.client.call("POST", f"/api/v1/vmeta/dataset/{dataset_id}/addFiles", data=file_data)
        except Exception as e:
            raise Exception(f"Error 2037: Failed to add files to dataset {dataset_id}: {e}") from e

    # --- Data Methods ---
    def search_data(self, project_id: str, collection_name: str, filter_data: dict = None) -> dict:
        """
        Searches data entries in a collection.

        Args:
            project_id (str): Project ID.
            collection_name (str): Collection name.
            filter_data (dict, optional): Filter criteria.

        Returns:
            dict: Search results.

        Raises:
            Exception: If search fails.
        """
        try:
            return self.client.call("POST", f"/api/v1/vmeta/project/{project_id}/data/{collection_name}/search", data=filter_data or {})
        except Exception as e:
            raise Exception(f"Error 2041: Failed to search data for {collection_name}: {e}") from e

    def get_data(self, project_id: str, collection_name: str, data_id: str) -> dict:
        """
        Retrieves a data entry by ID.

        Args:
            project_id (str): Project ID.
            collection_name (str): Collection name.
            data_id (str): Data entry ID.

        Returns:
            dict: Data record.

        Raises:
            Exception: If retrieval fails.
        """
        try:
            return self.client.call("GET", f"/api/v1/vmeta/project/{project_id}/data/{collection_name}/{data_id}")
        except Exception as e:
            raise Exception(f"Error 2042: Failed to get data {data_id}: {e}") from e

    def update_data(self, project_id: str, collection_name: str, data_id: str, update_data: dict) -> dict:
        """
        Updates a data entry.

        Args:
            project_id (str): Project ID.
            collection_name (str): Collection name.
            data_id (str): Data entry ID.
            update_data (dict): Update payload.

        Returns:
            dict: Updated data entry.

        Raises:
            Exception: If update fails.
        """
        try:
            return self.client.call("PATCH", f"/api/v1/vmeta/project/{project_id}/data/{collection_name}/{data_id}", data=update_data)
        except Exception as e:
            raise Exception(f"Error 2043: Failed to update data {data_id}: {e}") from e

    def delete_data(self, project_id: str, collection_name: str, data_id: str) -> dict:
        """
        Deletes a data entry.

        Args:
            project_id (str): Project ID.
            collection_name (str): Collection name.
            data_id (str): Data entry ID.

        Returns:
            dict: Deletion result.

        Raises:
            Exception: If deletion fails.
        """
        try:
            return self.client.call("DELETE", f"/api/v1/vmeta/project/{project_id}/data/{collection_name}/{data_id}")
        except Exception as e:
            raise Exception(f"Error 2044: Failed to delete data {data_id}: {e}") from e

    # --- Helper Methods ---

    def transfer_ownership(self, obj: dict, new_owner: dict, project_id: str = None) -> dict:
        """
        Transfers ownership and sets lastUpdatedUser for a collection or field object.

        Args:
            obj (dict): The original dictionary (collection or field).
            new_owner (dict): A dict with the 'owner' key holding the new owner structure.

        Returns:
            dict: A modified copy of the original object with updated ownership and cleaned metadata.
        """
        new_obj = deepcopy(obj)
        owner_data = new_owner['owner']
        owner_id = owner_data['_id']

        def recursive_cleanup(data):
            if isinstance(data, dict):
                keys_to_delete = []
                for key, value in data.items():
                    if key == 'owner' and isinstance(value, dict):
                        data[key] = deepcopy(owner_data)
                    elif key == 'lastUpdatedUser':
                        data[key] = owner_id
                    elif key == 'projectID':
                        if project_id is not None:
                            data[key] = project_id     
                    elif key in ['perms', 'restrictTo']:
                        keys_to_delete.append(key)
                    else:
                        recursive_cleanup(value)
                for key in keys_to_delete:
                    del data[key]
            elif isinstance(data, list):
                for item in data:
                    recursive_cleanup(item)
            return data
        return recursive_cleanup(new_obj)