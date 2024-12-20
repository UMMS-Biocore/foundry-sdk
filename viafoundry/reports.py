import pandas as pd
import os
import requests

class Reports:
    def __init__(self, client):
        self.client = client

    def fetch_report_data(self, report_id):
        """Fetch JSON data for a report."""
        endpoint = f"/api/run/v1/{report_id}/reports/"
        return self.client.call("GET", endpoint)

    def get_process_names(self, report_data):
        """Get unique process names."""
        return list({entry.get("processName") for entry in report_data["data"]})

    def get_file_names(self, report_data, process_name):
        """Get file names for a specific process."""
        processes = [
            entry for entry in report_data["data"] if entry.get("processName") == process_name
        ]
        if not processes:
            raise ValueError(f"Process '{process_name}' not found.")
        files = pd.DataFrame(processes[0]["children"])
        return files[["id", "processName", "name", "extension", "fileSize", "routePath"]]

    def download_file(self, report_data, process_name, file_name, download_dir=os.getcwd()):
        """Download a file from the API."""
        files = self.get_file_names(report_data, process_name)
        file_details = files[files["name"] == file_name]

        if file_details.empty:
            raise ValueError(f"File '{file_name}' not found in process '{process_name}'.")

        file_url = self.client.auth.hostname + file_details["routePath"].iloc[0]
        output_path = os.path.join(download_dir, file_name)

        response = requests.get(file_url, headers=self.client.auth.get_headers())
        response.raise_for_status()

        with open(output_path, "wb") as file:
            file.write(response.content)

        return output_path

    def get_all_files(self, report_data):
        """
        Extract all files across all processes for a specific report.
        :param report_data: JSON data containing the report.
        :return: DataFrame containing all files with metadata.
        """
        all_files = []
        for entry in report_data["data"]:
            process_name = entry.get("processName")
            for child in entry.get("children", []):
                child["processName"] = process_name
                all_files.append(child)

        if not all_files:
            raise ValueError("No files found in the report.")
            
        return pd.DataFrame(all_files)[["id", "processName", "name", "extension", "fileSize", "routePath"]]
