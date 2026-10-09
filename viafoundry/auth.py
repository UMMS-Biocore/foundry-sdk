import os
import re
import sys
import json
import getpass
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.viaenv")

# Session cookie names, current first. Servers before the Foundry Connect rebrand set only the
# legacy name; newer servers set the current one and still accept the legacy one on read.
SESSION_COOKIE_NAMES = ("foundry-connect-cookie", "viafoundry-cookie")

AUTHENTICATOR_CODE = re.compile(r"^\d{3}\s?\d{3}$")


class MfaError(Exception):
    """Sign-in needs a second factor that could not be completed."""


class Auth:
    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the Auth class.

        Args:
            config_path (str, optional): Path to the configuration file. Defaults to None.
        """
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config = self.load_config()
        self.hostname = self.config.get("hostname")  # Initialize hostname
        self.bearer_token = self.config.get("bearer_token")  # Bearer token

    def load_config(self) -> Dict:
        """Load configuration from the config file.

        Returns:
            Dict: The loaded configuration.
        """
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {}

    def save_config(self) -> None:
        """Save hostname and bearer token to the config file.
        """
        config = {
            "hostname": self.hostname,
            "bearer_token": self.bearer_token  # Save only the bearer token
        }
        # The file holds a bearer token, so only its owner may read it.
        fd = os.open(self.config_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump(config, f, indent=4)
        if os.name == "posix":
            os.chmod(self.config_path, 0o600)  # also tighten a file an older version created

    def configure(self, hostname: str, username: Optional[str] = None, password: Optional[str] = None, token: Optional[str] = None, identity_type: int = 1, redirect_uri: Optional[str] = None, mfa_code: Optional[str] = None, recovery_code: Optional[str] = None) -> None:
        """Prompt user for credentials if necessary and authenticate.

        Args:
            hostname (str): The hostname for authentication.
            username (str, optional): The username for authentication. Defaults to None.
            password (str, optional): The password for authentication. Defaults to None.
            token (str, optional): Pre-generated personal access token. Defaults to None.
            identity_type (int, optional): The identity type. Defaults to 1.
            redirect_uri (str, optional): The redirect URI. Defaults to "<hostname>/user".
            mfa_code (str, optional): The 6 digit code from your authenticator app, when your account
                uses multi-factor sign-in. Prompted for at a terminal when omitted.
            recovery_code (str, optional): A recovery code to use instead of an authenticator code.

        Raises:
            ValueError: If hostname or token is empty.
            MfaError: If the second factor is needed and could not be completed.
        """
        if not hostname or not hostname.strip():
            raise ValueError("Hostname cannot be empty")

        self.hostname = hostname

        # If token is provided, use it directly
        if token:
            if not token.strip():
                raise ValueError("Token cannot be empty")
            self.bearer_token = token
            self.save_config()
            return
        
        # Otherwise, use username/password authentication
        if not username or not password:
            username = input("Username: ")
            password = getpass.getpass("Password: ")
        
        # Validate username and password
        if not username or not username.strip():
            raise ValueError("Username cannot be empty")
        if not password or not password.strip():
            raise ValueError("Password cannot be empty")

        # Authenticate and retrieve the cookie token
        cookie_token = self.login(username, password, identity_type, redirect_uri, mfa_code=mfa_code, recovery_code=recovery_code)
        # Use cookie token to get bearer token
        self.bearer_token = self.get_bearer_token(cookie_token)
        self.save_config()
    
    def configure_token(self, hostname: str, token: str) -> None:
        """Configure authentication using a pre-generated personal access token.

        Args:
            hostname (str): The hostname for authentication.
            token (str): Pre-generated personal access token.
        
        Raises:
            ValueError: If hostname or token is empty.
        """
        if not hostname or not hostname.strip():
            raise ValueError("Hostname cannot be empty")
        if not token or not token.strip():
            raise ValueError("Token cannot be empty")
        
        self.hostname = hostname
        self.bearer_token = token
        self.save_config()

    def login(self, username: str, password: str, identity_type: int = 1, redirect_uri: Optional[str] = None, mfa_code: Optional[str] = None, recovery_code: Optional[str] = None) -> str:
        """Sign in and return the session cookie value.

        When the account uses multi-factor sign-in, the server answers the password step with a
        challenge, and the second factor (``mfa_code`` or ``recovery_code``) completes it. At a
        terminal the code is prompted for when neither is given.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
            identity_type (int, optional): The identity type. Defaults to 1.
            redirect_uri (str, optional): The redirect URI. Defaults to "<hostname>/user".
            mfa_code (str, optional): The 6 digit code from your authenticator app.
            recovery_code (str, optional): A recovery code to use instead of an authenticator code.

        Returns:
            str: The session cookie value.

        Raises:
            MfaError: If the second factor is needed and could not be completed.
        """
        if not self.hostname:
            raise ValueError("Hostname is not set. Please configure the SDK.")
        
        url = f"{self.hostname}/api/v1/auth/login"
        payload = {
            "username": username,
            "password": password,
            "identityType": identity_type,
            # A server checks this against its own address, so default to the configured host.
            "redirectUri": redirect_uri or f"{self.hostname.rstrip('/')}/user"
        }

        # One cookie jar for the whole sign-in, so the challenge cookie set by the password step
        # reaches the second factor step.
        http = requests.Session()
        response = http.post(url, json=payload)
        response.raise_for_status()

        challenge = self._json_body(response)
        if challenge.get("mfaRequired"):
            self._complete_second_factor(http, challenge.get("purpose"), mfa_code, recovery_code)

        for name in SESSION_COOKIE_NAMES:
            token = http.cookies.get(name)
            if token:
                return token
        raise ValueError("Sign-in succeeded but the server returned no session cookie.")

    @staticmethod
    def _json_body(response: requests.Response) -> Dict:
        try:
            body = response.json()
        except ValueError:
            return {}
        return body if isinstance(body, dict) else {}

    def _complete_second_factor(self, http: requests.Session, purpose: Optional[str], mfa_code: Optional[str], recovery_code: Optional[str]) -> None:
        """Answer the sign-in challenge with an authenticator code or a recovery code."""
        if purpose != "signin":
            raise MfaError(
                f"Your account must set up multi-factor sign-in first. Sign in once at {self.hostname} "
                "in a browser to add your authenticator app, then try again."
            )

        if not mfa_code and not recovery_code:
            if not sys.stdin or not sys.stdin.isatty():
                raise MfaError(
                    "Your account uses multi-factor sign-in. Pass mfa_code (the 6 digit code from your "
                    "authenticator app) or recovery_code, or configure the SDK with a personal access token."
                )
            entered = getpass.getpass("Authenticator code (or a recovery code): ").strip()
            if AUTHENTICATOR_CODE.match(entered):
                mfa_code = entered
            else:
                recovery_code = entered

        body = {"code": re.sub(r"\s", "", mfa_code)} if mfa_code else {"recoveryCode": recovery_code.strip()}
        # The legacy /api/auth/v1 mount on purpose: the server scopes the challenge cookie to the
        # /api/auth path, so a request under the canonical /api/v1/auth mount would not carry it.
        response = http.post(f"{self.hostname}/api/auth/v1/mfa/verify", json=body)
        if not response.ok:
            # The server answers {error, message}; the message is written for the user.
            message = self._json_body(response).get("message") or f"HTTP {response.status_code}"
            raise MfaError(f"Multi-factor sign-in failed: {message}")

    def calculate_expiration_date(self) -> str:
        """Calculate an expiration date one month from now.

        Returns:
            str: The expiration date in YYYY-MM-DD format.
        """
        return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    def get_bearer_token(self, cookie_token: str, name: str = "token") -> str:
        """Request a bearer token using the existing cookie token.

        Args:
            cookie_token (str): The cookie token for authentication.
            name (str, optional): The name of the token. Defaults to "token".

        Returns:
            str: The bearer token.
        """
        if not self.hostname:
            raise ValueError("Hostname is missing. Please configure the SDK.")

        url = f"{self.hostname}/api/v1/auth/personal-access-token"
        headers = {"Cookie": "; ".join(f"{name}={cookie_token}" for name in SESSION_COOKIE_NAMES)}
        payload = {"name": name, "expiresAt": self.calculate_expiration_date()}

        # Send POST request to get the bearer token
        response = requests.post(url, headers=headers, json=payload)
        # The server answers 404 when the Personal Access Token feature is off for this user,
        # which is per user and off by default. Say so instead of a bare Not Found.
        if response.status_code == 404:
            raise ValueError(
                "Signed in, but personal access tokens are not enabled for this account. "
                "Ask an administrator to enable the Personal Access Token feature for your user, then run configure again."
            )
        response.raise_for_status()

        data = response.json()
        bearer_token = data.get("token")
        if not bearer_token:
            raise ValueError(f"Bearer token not found in response (keys: {sorted(data)})")
        
        return bearer_token

    def get_headers(self) -> Dict:
        """Return headers with the bearer token.

        Returns:
            Dict: Headers containing the bearer token.
        """
        if not self.bearer_token:
            raise ValueError("Bearer token is missing. Please configure the SDK.")
        return {"Authorization": f"Bearer {self.bearer_token}"}
