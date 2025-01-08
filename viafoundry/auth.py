import os
import json
import requests
from datetime import datetime, timedelta

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.viaenv")

class Auth:
    def __init__(self, config_path=None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config = self.load_config()
        self.hostname = self.config.get("hostname")  # Initialize hostname
        self.bearer_token = self.config.get("bearer_token")  # Bearer token

    def load_config(self):
        """Load configuration from the config file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {}

    def save_config(self):
        """Save hostname and bearer token to the config file."""
        config = {
            "hostname": self.hostname,
            "bearer_token": self.bearer_token  # Save only the bearer token
        }
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)

    def configure(self, hostname, username=None, password=None, identity_type=1, redirect_uri="https://viafoundry.com/user"):
        """Prompt user for credentials if necessary and authenticate."""
        self.hostname = hostname
        if not username or not password:
            username = input("Username: ")
            password = input("Password: ")

        # Authenticate and retrieve the cookie token
        cookie_token = self.login(username, password, identity_type, redirect_uri)
        
        # Use cookie token to get bearer token
        self.bearer_token = self.get_bearer_token(cookie_token)
        self.save_config()

    def login(self, username, password, identity_type=1, redirect_uri="https://viafoundry.com/user"):
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

    def calculate_expiration_date(self):
        """Calculate an expiration date one month from now."""
        return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    def get_bearer_token(self, cookie_token, name="token"):
        """Request a bearer token using the existing cookie token."""
        if not self.hostname:
            raise ValueError("Hostname is missing. Please configure the SDK.")

        url = f"{self.hostname}/api/auth/v1/personal-access-token"
        headers = {"Cookie": f"viafoundry-cookie={cookie_token}"}
        payload = {"name": name, "expiresAt": self.calculate_expiration_date()}

        # Send POST request to get the bearer token
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        bearer_token = data.get("token")
        if not bearer_token:
            raise ValueError(f"Bearer token not found in response: {data}")
        
        return bearer_token

    def get_headers(self):
        """Return headers with the bearer token."""
        if not self.bearer_token:
            raise ValueError("Bearer token is missing. Please configure the SDK.")
        return {"Authorization": f"Bearer {self.bearer_token}"}
