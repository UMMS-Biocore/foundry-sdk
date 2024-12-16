import requests
from viafoundry.auth import Auth
from requests.exceptions import RequestException, MissingSchema
import logging

# Configure logging
logging.basicConfig(filename="viafoundry_errors.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


class ViaFoundryClient:
    def __init__(self, config_path=None):
        try:
            self.auth = Auth(config_path)
        except Exception:
            self._raise_error(101, "Failed to initialize authentication. Check your configuration file.")
        self.endpoints_cache = None  # Cache for discovered endpoints

    def configure_auth(self, hostname, username, password, identity_type=None, redirect_uri=None):
        """Configure authentication by setting up the token."""
        try:
            self.auth.configure(hostname, username, password, identity_type, redirect_uri)
        except MissingSchema:
            self._raise_error(104, f"Invalid hostname '{hostname}'. No scheme supplied. Did you mean 'https://{hostname}'?")
        except RequestException:
            self._raise_error(102, "Failed to configure authentication. Check your hostname and credentials.")
        except Exception:
            self._raise_error(999, "An unexpected error occurred while configuring authentication.")

    def discover(self):
        """Fetch all available endpoints from Swagger."""
        if self.endpoints_cache:
            return self.endpoints_cache

        hostname = self.auth.hostname
        if not hostname:
            self._raise_error(201, "Hostname is not configured. Please run the configuration setup.")

        url = f"{hostname}/api-docs/swagger.json?group=App"
        headers = self.auth.get_headers()

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            if "application/json" not in response.headers.get("Content-Type", ""):
                self._raise_error(203, f"Non-JSON response received from: {url}.")
            self.endpoints_cache = response.json().get("paths", {})
        except MissingSchema:
            self._raise_error(104, f"Invalid URL '{url}'. No scheme supplied. Did you mean 'https://{url}'?")
        except RequestException:
            self._raise_error(202, "Failed to fetch endpoints. Please verify your configuration.")
        except requests.exceptions.JSONDecodeError:
            self._raise_error(203, f"Failed to parse JSON response. Check the Swagger endpoint at: {url}.")
        except Exception:
            self._raise_error(999, "An unexpected error occurred while discovering endpoints.")
        return self.endpoints_cache

    def call(self, method, endpoint, params=None, data=None):
        """Send a request to a specific endpoint."""
        hostname = self.auth.hostname
        if not hostname:
            self._raise_error(201, "Hostname is not configured. Please run the configuration setup.")

        url = f"{hostname}{endpoint}"
        headers = self.auth.get_headers()

        try:
            response = requests.request(method.upper(), url, params=params, json=data, headers=headers)
            response.raise_for_status()

            if not response.text.strip():
                self._raise_error(204, f"Empty response from server for endpoint: {endpoint}.")
            if "application/json" not in response.headers.get("Content-Type", ""):
                self._raise_error(203, f"Non-JSON response received from endpoint: {endpoint}. Content: {response.text}")

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
