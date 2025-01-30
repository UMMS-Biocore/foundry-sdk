import pandas as pd
import os
import requests
import logging
import io
import mimetypes
from datetime import datetime
from IPython import get_ipython


class Reports:
    def __init__(self, client, enable_session_history=False):
        """
        Initialize the Reports.

        Args:
            enable_session_history (bool, optional): Enable or disable session history for reports. Defaults to False.
        """
        self.client = client
        self.enable_session_history = enable_session_history


    def fetch_report_data(self, report_id):
        """Fetch JSON data for a report and inject `file_dir` into all entries."""
        try:
            endpoint = f"/api/run/v1/{report_id}/reports/"
            report_data = self.client.call("GET", endpoint)

            # Recursively add `file_dir` to all entries
            def add_file_path(data):
                for entry in data:
                    # Inject `file_dir` into the current entry
                    entry["file_path"] = (
                        entry["routePath"].split("pubweb/")[-1]
                        if "pubweb/" in entry["routePath"]
                        else None
                    )
                    # Recursively process children if they exist
                    if "children" in entry and isinstance(entry["children"], list):
                        add_file_path(entry["children"])

            add_file_path(report_data.get("data", []))
            return report_data
        except Exception as e:
            self._raise_error(601, f"Failed to fetch report data for report ID '{report_id}': {e}")

    def get_process_names(self, report_data):
        """Get unique process names."""
        try:
            return list({entry.get("processName") for entry in report_data["data"]})
        except Exception as e:
            self._raise_error(602, f"Failed to extract process names: {e}")

    def get_file_names(self, report_data, process_name):
        """Get file names for a specific process."""
        try:
            processes = [
                entry for entry in report_data["data"] if entry.get("processName") == process_name
            ]
            if not processes:
                self._raise_error(603, f"Process '{process_name}' not found.")
            files = pd.DataFrame(processes[0]["children"])
    
            return files[["id", "processName", "name", "extension", "file_path", "fileSize", "routePath"]]
        except Exception as e:
            self._raise_error(604, f"Failed to get file names for process '{process_name}': {e}")

    def load_file(self, json_data, file_path, sep="\t"):
        """
        Load or download a file from a process.
        :param json_data: JSON data containing the report.
        :param process_name: The name of the process.
        :param file_name: The name of the file to load or download.
        :param sep: Separator for tabular files.
        :return: DataFrame if the file is tabular, or None for non-tabular files.
        """
        try:
            files = self.get_all_files(json_data)
            file_details = files[files["file_path"] == file_path]
            file_name = os.path.basename(file_path)

            if file_details.empty:
                self._raise_error(605, f"File '{file_name}' not found in the files of this report.")

            file_url = self.client.auth.hostname + file_details["routePath"].iloc[0]
            file_extension = file_details["extension"].iloc[0].lower()

            headers = self.client.auth.get_headers()
            response = requests.get(file_url, headers=headers)

            if response.status_code != 200:
                self._raise_error(606, f"Failed to fetch file: HTTP {response.status_code}")

            # Load as a DataFrame
            content = response.text
            if file_extension in ["csv", "tsv", "txt"]:
                return pd.read_csv(io.StringIO(content), sep=sep)

            return content  # Return raw content for non-tabular files

        except Exception as e:
            self._raise_error(607, f"Failed to load file '{file_name}': {e}")

    def download_file(self, report_data, file_path, download_dir=os.getcwd()):
        """Download a file from the API."""
        try:
            files = self.get_all_files(report_data)
            file_details = files[files["file_path"] == file_path]
            file_name = os.path.basename(file_path)

            if file_details.empty:
                self._raise_error(608, f"File '{file_name}' not found in the files of this report.")

            file_url = self.client.auth.hostname + file_details["routePath"].iloc[0]
            output_path = os.path.join(download_dir, file_name)

            response = requests.get(file_url, headers=self.client.auth.get_headers())
            if response.status_code != 200:
                self._raise_error(609, f"Failed to download file: HTTP {response.status_code}")

            with open(output_path, "wb") as file:
                file.write(response.content)

            return output_path
        except Exception as e:
            self._raise_error(610, f"Failed to download file '{file_name}': {e}")

    def get_all_files(self, report_data):
        """
        Extract all files across all processes for a specific report.
        :param report_data: JSON data containing the report.
        :return: DataFrame containing all files with metadata.
        """
        try:
            all_files = []
            for entry in report_data["data"]:
                process_name = entry.get("processName")
                for child in entry.get("children", []):
                    child["processName"] = process_name
                    all_files.append(child)

            if not all_files:
                self._raise_error(611, "No files found in the report.")

            return pd.DataFrame(all_files)[
                ["id", "processName", "file_path", "name", "extension", "fileSize", "routePath"]
            ]
        except Exception as e:
            self._raise_error(612, f"Failed to extract all files from report: {e}")

    def _raise_error(self, code, message):
        """Raise a categorized error with a specific code and message."""
        logging.error(f"Error {code}: {message}")  # Log the error
        raise RuntimeError(f"Error {code}: {message}")


    def upload_report_file(self, report_id, local_file_path, dir=None):
        """
        Upload a file to a specific report.

        Args:
            report_id (str): The ID of the report.
            local_file_path (str): The local path to the file being uploaded.
            dir (str, optional): Directory name for organizing files.

        Returns:
            dict or str: Response from the server.
        """
        try:
            # Fetch the latest attempt_id if not provided
            report_paths = self.get_all_report_paths(report_id)
            attempt_id = report_paths[0].split("/report-resources/")[1].split("/pubweb")[0]

            # Construct the upload endpoint
            upload_endpoint = f"/api/run/v1/{report_id}/reports/upload/{attempt_id}"

            # Guess the MIME type of the file
            mime_type, _ = mimetypes.guess_type(local_file_path)
            if not mime_type:
                mime_type = "application/octet-stream"  # Default to binary stream

            # Open the file in binary mode
            with open(local_file_path, "rb") as file:
                files = {"file": (local_file_path.split("/")[-1], file, mime_type)}
                data = {"dir": dir} if dir else {}

                # Perform the upload
                response = self.client.call("POST", upload_endpoint, files=files, data=data)

            return response
        except Exception as e:
            self._raise_error(602, f"Failed to upload file to report: {e}")
            
    def get_all_report_paths(self, report_id):
        """Get unique report directories and attempt IDs for a specific report.

        Args:
            report_id (str): The ID of the report.

        Returns:
            list: A list of unique report directories.

        Raises:
            Exception: If the API call fails or no reports are found.
        """
        try:
            # Define the API endpoint
            endpoint = f"/api/run/v1/{report_id}/reports"

            # Call the API to fetch report data
            response = self.client.call("GET", endpoint)
            reports = response.get("data", [])
            
            if not reports:
                raise ValueError("No reports found.")

            # Extract unique `routePath` entries
            unique_paths = {entry.get("routePath") for entry in reports if "routePath" in entry}
            return list(unique_paths)
        except Exception as e:
            self._raise_error(602, f"Failed to fetch report directories: {e}")
    
    def get_report_dirs(self, report_id):
        """
        Get possible directories following 'pubweb' in the routePath.

        Args:
            report_id (str): The ID of the report.

        Returns:
            list: A list of unique directories found after 'pubweb'.

        Raises:
            Exception: If the API call fails or no directories are found.
        """
        try:
            # Get all routePaths for the report
            all_paths = self.get_all_report_paths(report_id)

            if not all_paths:
                raise ValueError("No reports found.")

            # Extract directories after 'pubweb'
            report_dirs = set()
            for route_path in all_paths:
                if "pubweb/" in route_path:
                    dir_after_pubweb = route_path.split("pubweb/")[-1]
                    report_dirs.add(dir_after_pubweb)

            if not report_dirs:
                raise ValueError("No directories found after 'pubweb'.")

            return  report_dirs
        
        except Exception as e:
            self._raise_error(603, f"Failed to fetch possible directories: {e}")

    def upload_session_history(self, report_id, dir=None):
        """
        Upload the session history as a standalone file.

        Args:
            report_id (str): The ID of the report.
            dir (str, optional): Directory name for organizing files.

        Returns:
            dict or str: Response from the server.
        """
        try:
            if not self.enable_session_history:
                raise RuntimeError("Session history functionality is disabled.")

            # Prepare session history file
            history_file_path = self.prepare_session_history()
            # Upload session history only if the flag is enabled
            if self.enable_session_history:
                self.upload_report_file(report_id, history_file_path, dir)
            
            # Clean up the temporary history file
            os.remove(history_file_path)

        except Exception as e:
            raise Exception(f"Failed to upload session history: {e}")

    def prepare_session_history(self):
        """
        Prepare session history from the current Jupyter or IPython session.

        Returns:
            str: Path to the saved history file.
        """
        try:
            ipython = get_ipython()
            if ipython is None:
                raise EnvironmentError("Session history can only be prepared in IPython or Jupyter environments.")

            # Generate a filename with the current date and time
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file_path = f"session_history_{timestamp}.txt"

            # Save the session history to the file
            with open(history_file_path, "w") as history_file:
                ipython.magic(f"history -f {history_file_path}")

            return history_file_path
        except Exception as e:
            raise Exception(f"Failed to prepare session history: {e}")