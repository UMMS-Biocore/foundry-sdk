
# ViaFoundry SDK and CLI

The **ViaFoundry SDK and CLI** provide a powerful way to interact with ViaFoundry APIs. Whether you're a developer integrating with the API or a user looking for a simple command-line interface, this package has you covered.

---

## Installation

1. **Install via pip**:
   ```bash
   pip install viafoundry-sdk
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

### **1. Login to ViaFoundry**
Authenticate with your ViaFoundry account:
```bash
foundry login --hostname https://your-api-host.com --username your-username --password your-password
```

Options:
- `--hostname`: The URL of the ViaFoundry API.
- `--username`: Your username.
- `--password`: Your password.

---

### **2. Discover Endpoints**
List all available endpoints from the API:
```bash
foundry discover
```

---

### **3. Call an Endpoint**
Send a request to a specific endpoint:
```bash
foundry call --method GET --endpoint /v1/example --params '{"key": "value"}'
```

Options:
- `--method`: HTTP method (`GET`, `POST`, etc.).
- `--endpoint`: API endpoint path (e.g., `/v1/example`).
- `--params`: Optional query parameters in JSON format (e.g., `{"key": "value"}`).
- `--data`: Optional request body in JSON format (e.g., `{"key": "value"}`).

---

### **4. View Help**
For a list of available commands, run:
```bash
foundry --help
```

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

---

### **5. Call an Endpoint**
Send a request to a specific endpoint:
```python
response = client.call(
    method="POST",
    endpoint="/v1/process",
    data={"key": "value"}
)
print("Response:", response)
```

---

## Logging

Errors and debug information are logged to `viafoundry_errors.log` in the current working directory. Ensure this file is accessible for troubleshooting.

---


