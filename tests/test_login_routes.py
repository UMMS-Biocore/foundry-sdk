from unittest.mock import MagicMock, patch

from viafoundry.auth import Auth


def _auth(tmp_path):
    auth = Auth(config_path=str(tmp_path / "config"))
    auth.hostname = "https://foundry.example.org"
    return auth


def test_bearer_request_uses_the_web_app_route(tmp_path):
    auth = _auth(tmp_path)
    response = MagicMock()
    response.json.return_value = {"token": "abc"}
    with patch("viafoundry.auth.requests.post", return_value=response) as post:
        assert auth.get_bearer_token("cookie") == "abc"
    assert post.call_args.args[0] == "https://foundry.example.org/api/auth/v1/personal-access-token"


def test_login_redirect_defaults_to_the_configured_host(tmp_path):
    auth = _auth(tmp_path)
    session = MagicMock()
    session.post.return_value.json.return_value = {}
    session.cookies.get.return_value = "cookie"
    with patch("viafoundry.auth.requests.Session", return_value=session):
        auth.login("user", "pw")
    assert session.post.call_args.kwargs["json"]["redirectUri"] == "https://foundry.example.org/user"


def test_login_redirect_can_still_be_overridden(tmp_path):
    auth = _auth(tmp_path)
    session = MagicMock()
    session.post.return_value.json.return_value = {}
    session.cookies.get.return_value = "cookie"
    with patch("viafoundry.auth.requests.Session", return_value=session):
        auth.login("user", "pw", redirect_uri="https://other.example.org/user")
    assert session.post.call_args.kwargs["json"]["redirectUri"] == "https://other.example.org/user"
