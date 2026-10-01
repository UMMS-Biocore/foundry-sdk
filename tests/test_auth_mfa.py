"""Sign-in against a local stand-in for the server's auth endpoints.

The stand-in follows the server's cookie contract: the password step (on the canonical
/api/v1/auth mount) either sets the session cookie or answers {"mfaRequired": true} with a
challenge cookie scoped to /api/auth, and /api/auth/v1/mfa/verify trades that challenge plus a
code for the session cookie. The client's cookie jar applies the real path scoping, so these
tests fail if the second factor goes to a path the challenge cookie does not cover.
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from viafoundry.auth import Auth, MfaError

CHALLENGE = "challenge-abc"
SESSION = "session-xyz"
GOOD_CODE = "123456"
GOOD_RECOVERY = "abcd-efgh-ijkl"


class FakeServer(BaseHTTPRequestHandler):
    # Per test: {"mfa": None | "signin" | "enroll", "session_cookie": name, "calls": [...]}
    state: dict = {}

    def log_message(self, *args):
        pass

    def _cookies(self):
        jar = {}
        for part in (self.headers.get("Cookie") or "").split(";"):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                jar[k] = v
        return jar

    def _send(self, status, body, cookies=()):
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for cookie in cookies:
            self.send_header("Set-Cookie", cookie)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _session_cookie(self):
        return f"{self.state['session_cookie']}={SESSION}; Path=/; HttpOnly; SameSite=Lax"

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length) or b"{}")
        cookies = self._cookies()
        self.state["calls"].append((self.path, body, cookies))

        if self.path == "/api/v1/auth/login":
            if self.state["mfa"]:
                return self._send(200, {"mfaRequired": True, "purpose": self.state["mfa"]},
                                  [f"via_mfa_challenge={CHALLENGE}; Path=/api/auth; HttpOnly; SameSite=Lax"])
            return self._send(200, {"user": {"id": 1}}, [self._session_cookie()])

        if self.path == "/api/auth/v1/mfa/verify":
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self._send(415, {"error": "unsupported_media_type", "message": "json only"})
            if cookies.get("via_mfa_challenge") != CHALLENGE:
                return self._send(401, {"error": "challenge_expired", "message": "Your sign-in expired. Sign in again."})
            if body.get("code") == GOOD_CODE or body.get("recoveryCode") == GOOD_RECOVERY:
                return self._send(200, {"user": {"id": 1}, "next": "/"}, [self._session_cookie()])
            return self._send(401, {"error": "invalid_code", "message": "That code did not work."})

        if self.path == "/api/v1/auth/personal-access-token":
            if SESSION not in cookies.values():
                return self._send(401, {"error": "unauthenticated"})
            return self._send(200, {"token": "pat-from-server"})

        self._send(404, {})


@pytest.fixture
def server():
    FakeServer.state = {"mfa": None, "session_cookie": "foundry-connect-cookie", "calls": []}
    httpd = HTTPServer(("127.0.0.1", 0), FakeServer)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}", FakeServer.state
    httpd.shutdown()


@pytest.fixture
def auth(tmp_path):
    return Auth(config_path=str(tmp_path / "viaenv.json"))


@pytest.fixture
def no_tty(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False, raising=False)


def configure(auth, host, **kwargs):
    auth.configure(host, "user@example.org", "pw", **kwargs)
    return json.load(open(auth.config_path))


def test_without_mfa_current_cookie_name(server, auth):
    host, state = server
    saved = configure(auth, host)
    assert saved == {"hostname": host, "bearer_token": "pat-from-server"}
    assert [c[0] for c in state["calls"]] == ["/api/v1/auth/login", "/api/v1/auth/personal-access-token"]


def test_without_mfa_legacy_cookie_name(server, auth):
    host, state = server
    state["session_cookie"] = "viafoundry-cookie"
    assert configure(auth, host)["bearer_token"] == "pat-from-server"


def test_mfa_code_completes_sign_in(server, auth):
    host, state = server
    state["mfa"] = "signin"
    assert configure(auth, host, mfa_code=GOOD_CODE)["bearer_token"] == "pat-from-server"
    path, body, cookies = state["calls"][1]
    assert path == "/api/auth/v1/mfa/verify"
    assert body == {"code": GOOD_CODE}
    assert cookies["via_mfa_challenge"] == CHALLENGE


def test_recovery_code_completes_sign_in(server, auth):
    host, state = server
    state["mfa"] = "signin"
    assert configure(auth, host, recovery_code=GOOD_RECOVERY)["bearer_token"] == "pat-from-server"
    assert state["calls"][1][1] == {"recoveryCode": GOOD_RECOVERY}


def test_wrong_code_surfaces_server_message(server, auth):
    host, state = server
    state["mfa"] = "signin"
    with pytest.raises(MfaError, match="That code did not work"):
        configure(auth, host, mfa_code="000000")


def test_missing_code_without_terminal_explains(server, auth, no_tty):
    host, state = server
    state["mfa"] = "signin"
    with pytest.raises(MfaError, match="mfa_code"):
        configure(auth, host)
    assert len(state["calls"]) == 1


@pytest.mark.parametrize("entered,sent", [
    ("123 456", {"code": GOOD_CODE}),
    (GOOD_RECOVERY, {"recoveryCode": GOOD_RECOVERY}),
])
def test_prompts_at_a_terminal(server, auth, monkeypatch, entered, sent):
    host, state = server
    state["mfa"] = "signin"
    monkeypatch.setattr("sys.stdin.isatty", lambda: True, raising=False)
    monkeypatch.setattr("viafoundry.auth.getpass.getpass", lambda prompt: entered)
    assert configure(auth, host)["bearer_token"] == "pat-from-server"
    assert state["calls"][1][1] == sent


@pytest.mark.parametrize("purpose", ["enroll", "recovery_enroll"])
def test_enrollment_needs_the_browser(server, auth, purpose):
    host, state = server
    state["mfa"] = purpose
    with pytest.raises(MfaError, match="in a browser"):
        configure(auth, host, mfa_code=GOOD_CODE)
    assert len(state["calls"]) == 1
