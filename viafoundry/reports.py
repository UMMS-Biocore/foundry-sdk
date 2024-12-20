import pandas as pd
import os
import requests
import logging
import io


class Reports:
    def __init__(self, client):
        self.client = client

    def fetch_report_data(self, report_id):
        """Fetch JSON data for a report."""
        try:
            endpoint = f"/api/run/v1/{report_id}/reports/"
            return self.client.call("GET", endpoint)
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
            return files[["id", "processName", "name", "extension", "fileSize", "routePath"]]
        except Exception as e:
            self._raise_error(604, f"Failed to get file names for process '{process_name}': {e}")

    def load_file(self, json_data, process_name, file_name, sep="\t"):
        """
        Load or download a file from a process.
        :param json_data: JSON data containing the report.
        :param process_name: The name of the process.
        :param file_name: The name of the file to load or download.
        :param sep: Separator for tabular files.
        :return: DataFrame if the file is tabular, or None for non-tabular files.
        """
        try:
            files = self.get_file_names(json_data, process_name)
            file_details = files[files["name"] == file_name]

            if file_details.empty:
                self._raise_error(605, f"File '{file_name}' not found for process '{process_name}'.")

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

    def download_file(self, report_data, process_name, file_name, download_dir=os.getcwd()):
        """Download a file from the API."""
        try:
            files = self.get_file_names(report_data, process_name)
            file_details = files[files["name"] == file_name]

            if file_details.empty:
                self._raise_error(608, f"File '{file_name}' not found in process '{process_name}'.")

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
                ["id", "processName", "name", "extension", "fileSize", "routePath"]
            ]
        except Exception as e:
            self._raise_error(612, f"Failed to extract all files from report: {e}")

    def _raise_error(self, code, message):
        """Raise a categorized error with a specific code and message."""
        logging.error(f"Error {code}: {message}")  # Log the error
        raise RuntimeError(f"Error {code}: {message}")
