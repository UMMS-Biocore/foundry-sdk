import requests
from viafoundry.auth import Auth
from requests.exceptions import RequestException, MissingSchema
from viafoundry.reports import Reports
from viafoundry.process import Process
import logging

# Configure logging
logging.basicConfig(filename="viafoundry_errors.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


class ViaFoundryClient:
    def __init__(self, config_path=None, enable_session_history=False):
        """
        Initialize the ViaFoundryClient.

        Args:
            config_path (str, optional): Path to the configuration file.
            enable_session_history (bool, optional): Enable or disable session history for reports. Defaults to False.
        """
        try:
            self.auth = Auth(config_path)
            logging.info("Authentication initialized successfully.")
            self.reports = Reports(self, enable_session_history=enable_session_history)
            logging.info("Reports functionality initialized successfully.")
            self.process = Process(self)  # Add Process integration
            logging.info("Process functionality initialized successfully.")

        except Exception as e:
            logging.error("Initialization error", exc_info=True)
            self._raise_error(101, "Failed to initialize authentication. Check your configuration file.")
        self.endpoints_cache = None  # Cache for discovered endpoints

    def configure_auth(self, hostname, username, password, identity_type="1", redirect_uri="http://localhost/user"):
        """Configure authentication by setting up the token."""
        try:
            self.auth.configure(hostname, username, password, identity_type, redirect_uri)
        except MissingSchema:
            self._raise_error(104, f"Invalid hostname '{hostname}'. No scheme supplied. Did you mean 'https://{hostname}'?")
        except RequestException:
            self._raise_error(102, "Failed to configure authentication. Check your hostname and credentials.")
        except Exception:
            self._raise_error(999, "An unexpected error occurred while configuring authentication.")

    def discover(self, search=None, as_json=False):
        """
        Fetch all available endpoints from Swagger. Optionally filter endpoints by a search string
        or key=value format, and return the result in JSON format.
        
        Args:
            search (str): Filter endpoints containing a search string or in `key=value` format.
            as_json (bool): Return the output as a JSON-formatted string instead of a Python dictionary.
        
        Returns:
            dict or str: A dictionary or JSON-formatted string of endpoints.
        """
        if self.endpoints_cache:
            endpoints = self.endpoints_cache
        else:
            hostname = self.auth.hostname
            if not hostname:
                self._raise_error(201, "Hostname is not configured. Please run the configuration setup.")

            url = f"{hostname}/swagger.json"
            headers = self.auth.get_headers()

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                if "application/json" not in response.headers.get("Content-Type", ""):
                    self._raise_error(203, f"Non-JSON response received from: {url}.")
                self.endpoints_cache = response.json().get("paths", {})
                endpoints = self.endpoints_cache
            except MissingSchema:
                self._raise_error(104, f"Invalid URL '{url}'. No scheme supplied. Did you mean 'https://{url}'?")
            except RequestException:
                self._raise_error(202, "Failed to fetch endpoints. Please verify your configuration.")
            except requests.exceptions.JSONDecodeError:
                self._raise_error(203, f"Failed to parse JSON response. Check the Swagger endpoint at: {url}.")
            except Exception:
                self._raise_error(999, "An unexpected error occurred while discovering endpoints.")

        # Filter by search string or key=value
        if search:
            if "=" in search:
                key, value = search.split("=", 1)
                if key == "endpoint":
                    # Special case for 'endpoint', match against endpoint keys
                    filtered_endpoints = {
                        endpoint: details
                        for endpoint, details in endpoints.items()
                        if value.lower() in endpoint.lower()
                    }
                else:
                    # General key=value filtering
                    filtered_endpoints = {
                        endpoint: details
                        for endpoint, details in endpoints.items()
                        if any(value.lower() in str(detail.get(key, "")).lower() for method, detail in details.items())
                    }
            else:
                # General substring filtering
                filtered_endpoints = {
                    endpoint: details
                    for endpoint, details in endpoints.items()
                    if search.lower() in endpoint.lower()
                }
        else:
            filtered_endpoints = endpoints

        # Return as JSON string if requested
        if as_json:
            import json
            return json.dumps(filtered_endpoints, indent=4)

        return filtered_endpoints

    def call(self, method, endpoint, params=None, data=None, files=None):
        """Send a request to a specific endpoint."""
        hostname = self.auth.hostname
        #print(hostname)
        if not hostname:
            self._raise_error(201, "Hostname is not configured. Please run the configuration setup.")

        url = f"{hostname}{endpoint}"
        headers = self.auth.get_headers()

        try:
            # Debug request details
            # print(f"Request URL:{url}")
            # print(f"Request Method:{method}")
            # print(f"Request Params:{params}")
            # print(f"Request Data:{data}")
            # print(f"Request Files:{files}")
            # print(f"Request Headers:{headers}")

            if files:
                # Use 'data' for form-encoded fields and 'files' for file uploads
                response = requests.request(
                    method.upper(), url, params=params, data=data, files=files, headers=headers
                )
            else:
                # Standard request with JSON data
                response = requests.request(
                    method.upper(), url, params=params, json=data, headers=headers
                )

            response.raise_for_status()
            if "application/json" not in response.headers.get("Content-Type", ""):
                #self._raise_error(203, f"Non-JSON response received from endpoint: {endpoint}. Content: {response.text}")
                return response.text.strip()  # Return raw text response

            return response.json()
        except MissingSchema:
            self._raise_error(104, f"Invalid URL '{url}'. No scheme supplied. Did you mean 'https://{url}'?")
        except requests.exceptions.HTTPError:
            self._handle_http_error(response)
        except requests.exceptions.JSONDecodeError:
            self._raise_error(205, f"Failed to parse JSON response from endpoint: {endpoint}.")
        except RequestException:
            self._raise_error(206, "Request to endpoint failed. Please check your parameters or server configuration.")
        except Exception:
            self._raise_error(999, "An unexpected error occurred while calling the endpoint.")

    def _handle_http_error(self, response):
        """Categorize HTTP errors based on status codes."""
        status_code = response.status_code
        if status_code == 400:
            self._raise_error(302, "Bad Request: Check the request parameters or payload.")
        elif status_code == 401:
            self._raise_error(303, "Unauthorized: Ensure proper authentication.")
        elif status_code == 403:
            self._raise_error(304, "Forbidden: You do not have permission to access this resource.")
        elif status_code == 404:
            self._raise_error(305, "Not Found: The requested resource does not exist.")
        elif status_code == 500:
            self._raise_error(306, "Internal Server Error: Something went wrong on the server.")
        else:
            self._raise_error(307, f"Unexpected HTTP error occurred. Status code: {status_code}.")

    def _raise_error(self, code, message):
        """Raise a categorized error with a specific code and message."""
        logging.error(f"Error {code}: {message}")  # Log the error
        raise RuntimeError(f"Error {code}: {message}")
