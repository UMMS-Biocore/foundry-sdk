import os
import json
import requests

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.viaenv")

class Auth:
    def __init__(self, config_path=None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config = self.load_config()
        self.hostname = self.config.get("hostname")  # Initialize hostname
        self.token = self.config.get("token")

    def load_config(self):
        """Load configuration from the config file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {}

    def save_config(self):
        """Save hostname and token (cookie) to the config file."""
        config = {
            "hostname": self.hostname,
            "token": self.token  # Save the cookie token
        }
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)

    def configure(self, hostname, username=None, password=None, identity_type=1, redirect_uri="http://localhost"):
        """Prompt user for credentials if necessary and authenticate."""
        self.hostname = hostname
        if not username or not password:
            username = input("Username: ")
            password = input("Password: ")

        # Authenticate and retrieve the token (cookie)
        self.token = self.login(username, password, identity_type, redirect_uri)
        self.save_config()

    def login(self, username, password, identity_type, redirect_uri):
        """Authenticate and get the token from the Set-Cookie header."""
        if not self.hostname:
            raise ValueError("Hostname is not set. Please configure the SDK.")
        
        url = f"{self.hostname}/api/auth/v1/login"
        payload = {
            "username": username,
            "password": password,
            "identityType": identity_type,
            "redirectUri": redirect_uri
        }

        # Send POST request to authenticate
        response = requests.post(url, json=payload)
        response.raise_for_status()

        # Extract the 'Set-Cookie' header
        cookie_header = response.headers.get("Set-Cookie")
        if not cookie_header:
            raise ValueError(f"Cookie not found in response headers: {response.headers}")
        
        # Extract the token value from the cookie
        cookie_key = "viafoundry-cookie="
        start_index = cookie_header.find(cookie_key) + len(cookie_key)
        end_index = cookie_header.find(";", start_index)
        token = cookie_header[start_index:end_index]
        
        if not token:
            raise ValueError(f"Token not found in cookie: {cookie_header}")
        
        return token
  
    def get_headers(self):
        """Return headers with the token included as a cookie."""
        if not self.token:
            raise ValueError("Authentication token is missing. Please configure the SDK.")
        return {"Cookie": f"viafoundry-cookie={self.token}"}
