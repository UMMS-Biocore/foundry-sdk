# ViaFoundry SDK and CLI (v1.0.8)

The **ViaFoundry SDK and CLI** provide a powerful way to interact with ViaFoundry APIs. Whether you're a developer integrating with the API or a user looking for a simple command-line interface, this package has you covered.

---

## Table of Contents
- [Installation](#installation)
- [CLI Usage](#cli-usage)
  - [1. Configure the SDK](#1-configure-the-sdk)
  - [2. Discover Endpoints](#2-discover-endpoints)
    - [Usage](#usage)
    - [Filtering Capabilities](#filtering-capabilities)
    - [Free-Text Search](#free-text-search)
    - [Key-Value Search](#key-value-search)
    - [JSON Output](#json-output)
    - [Summary](#summary)
  - [3. Call an Endpoint](#3-call-an-endpoint)
  - [4. Reports Management](#4-reports-management)
    - [Fetch Report Data](#fetch-report-data)
    - [List Unique Processes in a Report](#list-unique-processes-in-a-report)
    - [List Files for a Specific Process](#list-files-for-a-specific-process)
    - [Download a Specific File](#download-a-specific-file)
    - [List All Files in a Report](#list-all-files-in-a-report)
  - [5. Example: Launch an App](#5-example-launch-an-app)
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
    - [Summary](#summary-sdk)
  - [5. Fetch Report Data](#5-fetch-report-data)
  - [6. List Processes in a Report](#6-list-processes-in-a-report)
  - [7. List Files for a Process](#7-list-files-for-a-process)
  - [8. Download a File](#8-download-a-file)
  - [9. List All Files in a Report](#9-list-all-files-in-a-report)

---
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

### **1. Configure the SDK**
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
List files for a specific process within a report:
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
foundry reports download-file REPORT_ID PROCESS_NAME FILE_NAME --download-dir /path/to/save
```

or

```bash
foundry reports download-file --reportID=REPORT_ID --processName=PROCESS_NAME --fileName=FILE_NAME --download-dir /path/to/save
```

#### **e. List All Files in a Report**
List all files across all processes in a report:
```bash
foundry reports list-all-files REPORT_ID
```

or

```bash
foundry reports list-all-files --reportID=REPORT_ID
```

---

### **5. Example: Launch an App**
Send a POST request to a specific endpoint to launch an app:
```bash
foundry call --endpoint /api/app/v1/call/1 --method POST --data '{"type": "standalone"}'
```

---
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

### **5. Fetch Report Data**
Fetch JSON data for a specific report:
```python
report_data = client.reports.fetch_report_data(report_id="12345")
```

---

### **6. List Processes in a Report**
List unique processes in the fetched report data:
```python
process_names = client.reports.get_process_names(report_data)
print("Processes:", process_names)
```

---

### **7. List Files for a Process**
List all files for a specific process in the report:
```python
files = client.reports.get_file_names(report_data, process_name="myProcess")
print(files)
```

---

### **8. Download a File**
Download a specific file from the report:
```python
client.reports.download_file(
    report_data,
    process_name="myProcess",
    file_name="example.txt",
    download_dir="/path/to/save"
)
```

---

### **9. List All Files in a Report**
List all files across all processes in the report:
```python
all_files = client.reports.get_all_files(report_data)
print(all_files)
```

---

## Summary
The enhanced `discover` function in the SDK allows you to:
- Filter API endpoints by free-text or key-value pairs.
- Retrieve results as a Python dictionary or JSON string.
- Focus your search on specific fields like `endpoint` or `description`.
- Access reports data and download them to use in further analysis

This makes it easier to programmatically explore and interact with the available API endpoints in ViaFoundry.

---
