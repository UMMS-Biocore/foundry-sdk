import os
import stat
import sys
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from viafoundry.auth import Auth
from viafoundry.bin.foundry import cli

posix_only = pytest.mark.skipif(sys.platform == "win32", reason="POSIX file modes")


def _mode(path):
    return stat.S_IMODE(os.stat(path).st_mode)


@posix_only
def test_save_config_creates_owner_only_file(tmp_path):
    path = tmp_path / "config"
    auth = Auth(config_path=str(path))
    auth.hostname = "https://example.org"
    auth.bearer_token = "abc"
    auth.save_config()
    assert _mode(path) == 0o600


@posix_only
def test_save_config_tightens_existing_file(tmp_path):
    path = tmp_path / "config"
    path.write_text("{}")
    os.chmod(path, 0o644)
    auth = Auth(config_path=str(path))
    auth.hostname = "https://example.org"
    auth.bearer_token = "abc"
    auth.save_config()
    assert _mode(path) == 0o600


def test_interactive_token_prompt_is_hidden(tmp_path):
    value = "not-a-real-token-123"
    with patch.object(Auth, "configure_token") as configure_token:
        result = CliRunner().invoke(
            cli,
            ["--config", str(tmp_path / "config"), "configure", "--hostname", "https://example.org"],
            input=f"1\n{value}\n",
        )
    assert result.exit_code == 0, result.output
    configure_token.assert_called_once_with("https://example.org", value)
    assert value not in result.output
