from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from click.testing import CliRunner

patcher = patch("telethon.TelegramClient")
patcher.start()

from tegracli.main import cli


@pytest.fixture
def runner():
    """Fixture for click.CliRunner"""
    return CliRunner()


def test_help_prompt(runner: CliRunner, tmpdir: Path):
    """Should show help if no args present"""
    with runner.isolated_filesystem(tmpdir):
        result = runner.invoke(cli, [""])

        assert result.exit_code == 2


def test_configuration_present(runner: CliRunner, tmp_path: Path):
    """Should not throw if a configuration file is present"""
    with runner.isolated_filesystem(temp_dir=tmp_path) as temp_dir:

        conf_file = Path(temp_dir) / "tegracli.conf.yml"

        with conf_file.open("w") as config:
            yaml.dump(
                {
                    "api_id": 123456,
                    "api_hash": "wahgi231kmdma91",
                    "session_name": "test",
                },
                config,
            )

        result = runner.invoke(cli, ["get", "channel"])

        assert conf_file.exists()
        assert not result.exception
        assert result.exit_code == 0


def test_configuration_missing(runner: CliRunner, tmpdir: Path):
    """Should fail if no config is present in the current directory"""
    with runner.isolated_filesystem(tmpdir):
        result = runner.invoke(cli, ["get", "channel"])

        assert result.exit_code == 127


def test_search(runner: CliRunner):
    """Should get search results for specified terms"""

    result = runner.invoke(cli, ["search", "term"])

    assert result.exit_code == 0


patcher.stop()
