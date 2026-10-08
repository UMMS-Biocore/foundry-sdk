import os
import stat
import sys

import pytest

from viafoundry.auth import Auth

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

