# ViaFoundry SDK and CLI (v1.0.12)

The **ViaFoundry SDK and CLI** provide a powerful way to interact with ViaFoundry APIs. Whether you're a developer integrating with the API or a user looking for a simple command-line interface, this package has you covered.

---

## Table of Contents
- [Installation](#installation)
- [CLI Usage](#cli-usage)
  - [1. Configure the CLI or SDK](#1-configure-the-cli-or-sdk)
  - [2. Discover Endpoints](#2-discover-endpoints)
    - [Usage](#usage)
    - [Filtering Capabilities](#filtering-capabilities)
    - [Free-Text Search](#free-text-search)
    - [Key-Value Search](#key-value-search)
    - [JSON Output](#json-output)
    - [Summary](#summary)
  - [3. Call an Endpoint](#3-call-an-endpoint)
  - [4. Reports Management](#4-reports-management)
    - [Fetch Report Data](#a-fetch-report-data)
    - [List Unique Processes in a Report](#b-list-unique-processes-in-a-report)
    - [List Files for a Specific Process](#c-list-files-for-a-specific-process)
    - [Download a Specific File](#d-download-a-specific-file)
    - [List All Files in a Report](#e-list-all-files-in-a-report)
    - [Get directories in a Report to upload Files](#f-get-directories-in-a-report-to-upload-files)
    - [Upload a File to a Report](#g-upload-a-file-to-a-report)
  - [5. Example: Launch an App](#5-example-launch-an-app)
  - [6. Process Management](#6-process-management)
    - [List All Processes](#list-all-processes)
    - [Get Process Details](#get-Process-Details)
    - [Get Revisions for a Process](#get-Revisions-for-a-process)
    - [Check Process Usage](#check-process-usage)
    - [Duplicate a Process](#duplicate-a-process)
    - [Create a Menu Group](#create-a-menu-group)
    - [Create a Process](#create-a-process)
    - [Update a Process](#update-a-process)
    - [Delete a Process](#delete-a-process)
    - [Get Parameters for a Pipeline](#get-parameters-for-a-pipeline)
    - [List All Parameters](#list-all-parameters)
    - [Create a Parameter](#create-a-parameter)
    - [Update a Parameter](#update-a-parameter)
    - [Delete a Parameter](#delete-a-parameter)
- [Logging](#logging)
- [SDK Usage](#sdk-usage)
  - [1. Import the SDK](#1-import-the-sdk)
  - [2. Initialize the Client](#2-initialize-the-client)
  - [3. Authenticate and Configure](#3-authenticate-and-configure)
  - [4. Discover Endpoints](#4-discover-endpoints-sdk)
    - [Usage](#usage-sdk)
    - [Free-Text Search](#free-text-search-sdk)
    - [Key-Value Search](#key-value-search-sdk)
    - [JSON Output](#json-output-sdk)
  - [5. Reports Managment](#5-reports-management)
    - [Fetch Report Data](#fetch-report-data)
    - [List Processes in a Report](#list-processes-in-a-report)
    - [List Files for a Process](#list-files-for-a-process)
    - [Download a File](#download-a-file)
    - [List All Files in a Report](#list-all-files-in-a-report)
    - [Upload report files](#upload-report-files)
    - [Get report dirs](#get-report-dirs)
    - [Get all report paths](#get-all-report-paths)
  - [6. Process Managment SDK](#6-process-management-sdk)
    - [List All Processes](#list-all-processes-sdk)
    - [Get Process Details](#get-Process-Details-sdk)
    - [Get Revisions for a Process](#get-Revisions-for-a-process-sdk)
    - [Check Process Usage](#check-process-usage-sdk)
    - [Duplicate a Process](#duplicate-a-process-sdk)
    - [Create a Menu Group](#create-a-menu-group-sdk)
    - [Create a Process](#create-a-process-sdk)
    - [Update a Process](#update-a-process-sdk)
    - [Delete a Process](#delete-a-process-sdk)
    - [Get Parameters for a Pipeline](#get-parameters-for-a-pipeline-sdk)
    - [List All Parameters](#list-all-parameters-sdk)
    - [Create a Parameter](#create-a-parameter-sdk)
    - [Update a Parameter](#update-a-parameter-sdk)
    - [Delete a Parameter](#delete-a-parameter-sdk)
  - [Summary](#summary)

---

## Installation

1. **Install via pip**:
   ```bash
   pip install viafoundry_sdk
   ```

2. **Verify Installation**:
   - For CLI:
     ```bash
     foundry --help
     ```
   - For SDK:
     Open a Python interpreter and ensure the package is importable:
     ```python
     import viafoundry
     ```

---

## CLI Usage

The CLI provides quick access to ViaFoundry functionalities without needing to write code. Below are some common commands.

```mermaid
graph LR
    subgraph CLI
        direction LR
        client[CLI Entry Point]
        config[Configure CLI]
        discover[Discover Endpoints]
        callAPI[Call API]
        anyAPI[Call Any API Endpoint]
        reports[Report Group]
        process[Process Group]

        client --> config 
        client --> discover
        client --> callAPI
        callAPI --> anyAPI
        callAPI --> reports
        callAPI --> process
    end
```

### **1. Configure the CLI or SDK**
Authenticate with your ViaFoundry account:
```bash
foundry configure
```

or

```bash
foundry configure --hostname https://your-api-host.com --username your-username --password your-password
```

Options:
- `--hostname`: The URL of the ViaFoundry API.
- `--username`: Your username.
- `--password`: Your password.

---


### **2. Discover Endpoints**

The `discover` command in the ViaFoundry CLI has been enhanced to support filtering of API endpoints. This feature allows users to narrow down the list of endpoints based on specific search criteria.

---

## Usage

### Basic Command
```bash
foundry discover [OPTIONS]
```

### Options
- `--as-json`: Output the filtered results in JSON format.
- `--search`: Search term to filter endpoints. Supports free-text or key-value format.

---

## Filtering Capabilities

### Free-Text Search
Search across all fields (`endpoint`, `method`, and `description`) using a case-insensitive match.

#### Example:
```bash
foundry discover --search "reports"
```

#### Output:
```plaintext
Available API Endpoints:

Endpoint: /run/v1/{runId}/reports
Method: get
Description: 'View the metdata and resource paths for run reports'

Endpoint: /run/v1/{runId}/reports-dirs
Method: get
Description: 'Upload report directories'

Endpoint: /run/v1/{runId}/reports/upload/:runUUID
Method: post
Description: 'list report directories'
Data to send: {
    "type": "object",
    "properties": {
        "dir": {
            "type": "string",
            "description": "The path to the report directory",
            "example": "/path/to/report"
        }
    },
    "additionalProperties": false
}
```

---

### Key-Value Search
Target specific fields by specifying a `key=value` pair.

#### Supported Keys:
- `endpoint`: Filters based on the endpoint path.
- `description`: Filters based on the description text.

#### Example 1: Search in Endpoint Field
```bash
foundry discover --search "endpoint=reports"
```

#### Example 2: Search in Description Field
```bash
foundry discover --search "description=parameters"  
```

---

## JSON Output
Add the `--as-json` flag to get the filtered results in JSON format.

#### Example:
```bash
foundry discover --as-json --search "reports"
```

---

## Summary
The enhanced `discover` command allows you to:
- Filter API endpoints by free-text or key-value pairs.
- View results in human-readable text or JSON format.
- Customize your search to focus on specific fields such as `endpoint` or `description`.

---

---

### **3. Call an Endpoint**
Send a request to a specific endpoint:
```bash
foundry call --method GET --endpoint /api/v1/example --params '{"key": "value"}'
```

Options:
- `--method`: HTTP method (`GET`, `POST`, etc.).
- `--endpoint`: API endpoint path (e.g., `/api/v1/example`).
- `--params`: Optional query parameters in JSON format (e.g., `{"key": "value"}`).
- `--data`: Optional request body in JSON format (e.g., `{"key": "value"}`).

---

### **4. Reports Management**
Work with reports using the `foundry reports` command group.

```mermaid
graph LR
    subgraph Reports
        direction LR
        fetch[Fetch Report Data]
        listProcesses[List Processes in Report]
        listFiles[List Files in Process]
        downloadFile[Download a File]
        uploadFile[Upload a File to Report]
        getReportDirs[Get Report Directories]

        fetch --> listProcesses
        listProcesses --> listFiles
        listFiles --> downloadFile
        listFiles --> uploadFile
        listFiles --> getReportDirs
    end
```
#### **a. Fetch Report Data**
Fetch JSON data for a report:
```bash
foundry reports fetch REPORT_ID
```

or

```bash
foundry reports fetch --reportID=REPORT_ID
```

#### **b. List Unique Processes in a Report**
List all unique processes in a report:
```bash
foundry reports list-processes REPORT_ID
```

or

```bash
foundry reports list-processes --reportID=REPORT_ID
```

#### **c. List Files for a Specific Process**
List files to get file paths for a specific process within a report:
```bash
foundry reports list-files REPORT_ID PROCESS_NAME
```

or

```bash
foundry reports list-files --reportID=REPORT_ID --processName=PROCESS_NAME
```

#### **d. Download a Specific File**
Download a file from a report:
```bash
foundry reports download-file REPORT_ID FILE_PATH --download-dir /path/to/save
```

or

```bash
foundry reports download-file --reportID=REPORT_ID --filePath=FILE_PATH --download-dir /path/to/save
```

#### **e. List All Files in a Report**
List all files across all processes in a report.
```bash
foundry reports list-all-files REPORT_ID
```

or

```bash
foundry reports list-all-files --reportID=REPORT_ID
```

---
### **f. Get directories in a Report to upload Files**
You can list possible directories in the report section that you can use while uploading files using the CLI:

```bash
foundry reports get-report-dirs REPORT_ID

```
or

```bash
foundry reports get-report-dirs --reportID REPORT_ID
```


### **g. Upload a File to a Report**

You can upload a file to a specific report using the CLI:

Options:
- `--reportID` TEXT   Report ID (alternative to positional argument).
- `--filePath` PATH   Local file path (alternative to positional argument).
- `--remoteDir` TEXT  Directory name for organizing files (alternative to
                    positional argument).

```bash
viafoundry upload-report-file REPORT_ID FILE_PATH REPORT-DIR
```

or 

```bash
viafoundry upload-report-file --reportID REPORT_ID --filePath FILE_PATH remoteDir REMOTE-DIR
```

Replace REPORT_ID with the target report’s ID and FILE_PATH with the path to the file you want to upload. Use the --dir option to specify a directory.

---

### **5. Example: Launch an App**
Send a POST request to a specific endpoint to launch an app:
```bash
foundry call --endpoint /api/app/v1/call/1 --method POST --data '{"type": "standalone"}'
```
### **6. Process Management**

Manage processes with commands like listing, creating, updating, and deleting processes.

```mermaid
graph LR
    subgraph Processes
        direction LR
        processesCLI[Processes]
        listProcessesCLI[List Processes]
        getProcessCLI[Get Process Details]
        getRevisionsCLI[Get Process Revisions]
        checkUsageCLI[Check Process Usage]
        duplicateProcessCLI[Duplicate Process]
        menuCLI[Menus]
        createMenuCLI[Create Menu]
        listMenuCLI[List Menu]
        updateMenuCLI[Update Menu]
        createProcessCLI[Create Process]
        updateProcessCLI[Update Process]
        deleteProcessCLI[Delete Process]

        processesCLI --> createProcessCLI 
        processesCLI --> listProcessesCLI
        processesCLI --> updateProcessCLI
        processesCLI --> deleteProcessCLI
        listProcessesCLI --> getProcessCLI
        getProcessCLI --> getRevisionsCLI
        getProcessCLI --> checkUsageCLI
        getProcessCLI --> duplicateProcessCLI
        menuCLI --> createMenuCLI
        menuCLI --> listMenuCLI
        menuCLI --> updateMenuCLI
    end
```

#### List All Processes
```bash
foundry process list-processes
```
#### Get Process Details
```bash
foundry process get-process <process_id>
# Or
foundry process get-process --processID <process_id>
```

#### Get Revisions for a Process
```bash
foundry process get-revisions <process_id>
# Or
foundry process get-revisions --processID <process_id>
```

#### Check Process Usage
```bash
foundry process check-usage <process_id>
# Or
foundry process check-usage --processID <process_id>
```

#### Duplicate a Process
```bash
foundry process duplicate-process <process_id>
# Or
foundry process duplicate-process --processID <process_id>
```

#### Create a Menu Group
```bash
foundry process create-menu-group <menu_name>
# Or
foundry process create-menu-group --menuName <menu_name>
```

#### Create a Process
Pass the process data as a JSON file:
```bash
foundry process create-process <path_to_json>
# Or
foundry process create-process --processData <path_to_json>
```

#### Update a Menu Group
```bash
foundry process update-menu-group <menu_group_id> <menu_name>
# Or
foundry process update-menu-group --menuGroupID <menu_group_id> --menuName <menu_name>
```

#### Update a Process
Pass the updated process data as a JSON file:
```bash
foundry process update-process <process_id> <path_to_json>
# Or
foundry process update-process --processID <process_id> --processData <path_to_json>
```

#### Delete a Process
```bash
foundry process delete-process <process_id>
# Or
foundry process delete-process --processID <process_id>
```

#### Get Parameters for a Pipeline
```bash
foundry process get-pipeline-parameters <pipeline_id>
# Or
foundry process get-pipeline-parameters --pipelineID <pipeline_id>
```

#### List All Parameters
```bash
foundry process list-parameters
```

#### Create a Parameter
Pass the parameter data as a JSON file:
```bash
foundry process create-parameter <path_to_json>
# Or
foundry process create-parameter --parameterData <path_to_json>
```

#### Update a Parameter
Pass the updated parameter data as a JSON file:
```bash
foundry process update-parameter <parameter_id> <path_to_json>
# Or
foundry process update-parameter --parameterID <parameter_id> --parameterData <path_to_json>
```

#### Delete a Parameter
```bash
foundry process delete-parameter <parameter_id>
# Or
foundry process delete-parameter --parameterID <parameter_id>
```

---

## Logging

Errors and debug information are logged to `viafoundry_errors.log` in the current working directory. Ensure this file is accessible for troubleshooting.

---

## SDK Usage

The SDK allows developers to programmatically interact with ViaFoundry APIs. Below are some examples.

### **1. Import the SDK**
```python
from viafoundry.client import ViaFoundryClient
```

---

### **2. Initialize the Client**
Provide the path to your configuration file or set up authentication manually:
```python
client = ViaFoundryClient(config_path="path/to/config.json")
```

Example `config.json`:
```json
{
    "hostname": "https://your-api-host.com",
    "token": "your-auth-token"
}
```

If you want to enable recording session while working in J

If you already authenticated using CLI or want to use default file (~/.viaenv). You can use like below.

```python
client = ViaFoundryClient()
```
---

### **3. Authenticate and Configure**
Alternatively, configure the client programmatically:
```python
client.configure_auth(
    hostname="https://your-api-host.com",
    username="your-username",
    password="your-password"
)
```

---

### **4. Discover Endpoints**
Retrieve a list of available API endpoints:
```python
endpoints = client.discover()
print("Discovered Endpoints:", endpoints)
```

The `discover` function in the ViaFoundry SDK has been enhanced to support filtering of API endpoints. This feature allows developers to programmatically narrow down the list of endpoints based on specific search criteria.

---

## Usage

### Function Signature
```python
def discover(self, search=None, as_json=False):
    """
    Discover available API endpoints with optional filtering.

    Parameters:
        search (str): Search term to filter endpoints. Supports free-text or 'key=value' format.
        as_json (bool): If True, return the filtered results as JSON.

    Returns:
        dict or str: Filtered endpoints as a dictionary (default) or JSON string if as_json is True.
    """
```

### Parameters
- `search`: 
  - **Free-text search**: Searches across all fields (`endpoint`, `method`, and `description`) using a case-insensitive match.
  - **Key-value search**: Targets specific fields such as `endpoint` or `description`.
- `as_json`: If `True`, the function returns the results in JSON format.

---

## Examples

### Free-Text Search
Search across all fields using a case-insensitive match.

#### Code:
```python
from viafoundry.client import ViaFoundryClient
client = ViaFoundryClient()
filtered_endpoints = client.discover(search="reports")
for endpoint, methods in filtered_endpoints.items():
    for method, details in methods.items():
        print(f"Endpoint: {endpoint}")
        print(f"Method: {method}")
        print(f"Description: {details.get('description', 'No description available')}")
```

#### Output:
```plaintext
Endpoint: /run/v1/{runId}/reports
Method: get
Description: View the metdata and resource paths for run reports
```

---

### Key-Value Search
Target specific fields using `key=value` format.

#### Code:
```python
# Search in the 'endpoint' field
filtered_endpoints = client.discover(search="endpoint=reports")
print(filtered_endpoints)

# Search in the 'description' field
filtered_endpoints = client.discover(search="description=logs")
print(filtered_endpoints)
```

---

### JSON Output
Get the filtered results in JSON format by setting `as_json=True`.

#### Code:
```python
filtered_endpoints_json = client.discover(search="logs", as_json=True)
print(filtered_endpoints_json)
```

### **5. Report section**

### **Fetch Report Data**
Fetch JSON data for a specific report:
```python
report_data = client.reports.fetch_report_data(report_id="12345")
```

---

### **List Processes in a Report**
List unique processes in the fetched report data:
```python
process_names = client.reports.get_process_names(report_data)
print("Processes:", process_names)
```

---

### **List Files for a Process**
List all files for a specific process in the report:
```python
files = client.reports.get_file_names(report_data, process_name="myProcess")
print(files)
```
---

### **Load a File**
Download a specific file from the report:
```python
loaded_data = client.reports.load_file(
    report_data,
    file_path="dir/example.txt"
)
print(loaded_data)
```

---

### **Download a File**
Download a specific file from the report:
```python
client.reports.download_file(
    report_data,
    file_path="dir/example.txt",
    download_dir="/path/to/save"
)
```

---

### **List All Files in a Report**
List all files across all processes in the report:
```python
all_files = client.reports.get_all_files(report_data)
print(all_files)
```
---

### **Upload report files**

Uploads a file to a specific report and organizes it in a specified directory. Be sure to learn how to retrieve the upload directory from #11.

#### Function Definition
```python
def upload_report_file(self, report_id, local_file_path, dir=None):
    \"\"\"Upload a file to a specific report.

    Args:
        report_id (str): The ID of the report.
        local_file_path (str): The local path to the file being uploaded.
        dir (str, optional): Directory name for organizing files.

    Returns:
        dict or str: Response from the server.
    \"\"\"
```

#### Example Usage
```python
client = ViaFoundryClient()
response = client.reports.upload_report_file(
    report_id="1",
    local_file_path="/path/to/your/file.csv",
    dir="summary"
)
print("Upload Response:", response)
```

#### Expected Output
```plaintext
Upload Response: OK
```

---

### **Get report dirs**

Fetches unique directories from a report after the `pubweb` segment in the `routePath`.

#### Function Definition
```python
def get_report_dirs(self, report_id):
    \"\"\"Get possible directories following 'pubweb' in the routePath.

    Args:
        report_id (str): The ID of the report.

    Returns:
        list: A list of unique directories found after 'pubweb'.
    \"\"\"
```

#### Example Usage
```python
client = ViaFoundryClient()
directories = client.reports.get_report_dirs("1")
print("Directories:", directories)
```

#### Expected Output
```json
{
    "directories": [
        "salmon_count",
        "star_count",
        "kallisto_count"
    ]
}
```

---

### **Get all report paths**

Fetches all `routePath` values from a specific report.

#### Function Definition
```python
def get_all_report_paths(self, report_id):
    \"\"\"Get all routePath values for a specific report.

    Args:
        report_id (str): The ID of the report.

    Returns:
        list: A list of all routePath values.
    \"\"\"
```

#### Example Usage
```python
client = ViaFoundryClient()
all_paths = client.reports.get_all_report_paths("1")
print("Route Paths:", all_paths)
```

#### Expected Output
```plaintext
Route Paths: [
    "/report-resources/dir1/pubweb/salmon_count",
    "/report-resources/dir1/pubweb/star_count",
    "/report-resources/dir1/pubweb/kallisto_count"
]
```

---

### **6. Process Management SDK**

#### Initialize the SDK
```python
from viafoundry.client import ViaFoundryClient

client = ViaFoundryClient(config_path="path_to_config.json")
process = client.process
```

#### List All Processes SDK
```python
processes = process.list_processes()
print(processes)
```

#### Get Process Details SDK
```python
process_details = process.get_process(process_id="12345")
print(process_details)
```

#### Get Process Revisions SDK
```python
revisions = process.get_process_revisions(process_id="12345")
print(revisions)
```

#### Check Process Usage SDK
```python
usage = process.check_process_usage(process_id="12345")
print(usage)
```

#### Duplicate a Process SDK
```python
duplicate_response = process.duplicate_process(process_id="12345")
print(duplicate_response)
```

#### Create a Menu Group SDK
```python
response = process.create_menu_group(name="New Menu Group")
print(response)
```

#### Create a Process SDK
```python
process_data = {
    "name": "Example Process",
    "summary": "An example process",
    "menuGroupId": 1,
    # Additional fields...
}
response = process.create_process(process_data=process_data)
print(response)
```

#### Update a Menu Group SDK
```python
response = process.update_menu_group(menu_group_id=1, name="Updated Menu Group")
print(response)
```

#### Update a Process SDK
```python
updated_data = {
    "name": "Updated Process",
    "summary": "Updated description",
    # Additional fields...
}
response = process.update_process(process_id="12345", process_data=updated_data)
print(response)
```

#### Delete a Process SDK
```python
response = process.delete_process(process_id="12345")
print(response)
```

#### Get Pipeline Parameters SDK
```python
parameters = process.get_pipeline_parameters(pipeline_id="67890")
print(parameters)
```

#### List All Parameters SDK
```python
parameters = process.list_parameters()
print(parameters)
```

#### Create a Parameter SDK
```python
parameter_data = {
    "name": "Parameter Name",
    "qualifier": "file",
    "fileType": "fasta",
}
response = process.create_parameter(parameter_data=parameter_data)
print(response)
```

#### Update a Parameter SDK
```python
updated_parameter = {
    "name": "Updated Parameter Name",
    "qualifier": "file",
    "fileType": "fastq",
}
response = process.update_parameter(parameter_id="123", parameter_data=updated_parameter)
print(response)
```

#### Delete a Parameter SDK
```python
response = process.delete_parameter(parameter_id="123")
print(response)
```
---

## Summary
The enhanced `discover` function in the SDK allows you to:
- Filter API endpoints by free-text or key-value pairs.
- Retrieve results as a Python dictionary or JSON string.
- Focus your search on specific fields like `endpoint` or `description`.
- Access reports data and upload/download them to use in further analysis in the report section
- Access process section and add remove parameters, processes and versions of the processes.

This makes it easier to programmatically explore and interact with the available API endpoints in ViaFoundry.

---
