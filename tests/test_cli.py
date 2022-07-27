""" # Command Line Interface Tests

This test suite tests the program's CLICK interface.

Tests should be run with click.CliRunner.

"""

# pylint: disable=redefined-outer-name
# pylint: disable=wrong-import-position

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from click.testing import CliRunner

from tegracli.group import Group

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
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Show this message and exit." in result.stdout


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
        print(result.stdout)
        assert conf_file.exists()
        assert not result.exception
        assert result.exit_code == 0


def test_configuration_missing(runner: CliRunner, tmpdir: Path):
    """Should fail if no config is present in the current directory"""
    with runner.isolated_filesystem(tmpdir):
        result = runner.invoke(cli, ["get", "channel"])
        print(result.stdout)
        assert result.exit_code == 127


def test_account_group_creation(runner: CliRunner, tmp_path: Path):
    """Should create a directory named by user input, read in a file with tg-accounts,
    resolve those user names and save messages by user in a jsonl-file.

    I.e. a call to this command would look like this:
    `tegracli group init --read_file account_list.csv my_little_account_list` to
    load a account list from a file and write the configuration file to disk.
    """

    with runner.isolated_filesystem(temp_dir=tmp_path) as temp_dir:
        conf_file = Path(temp_dir) / "tegracli.conf.yml"
        list_file = Path(temp_dir) / "account_list.csv"
        r_folder = Path(temp_dir) / "my_little_account_list/"
        r_file = r_folder / "tegracli_group.conf.yml"

        # fake credentials
        with conf_file.open("w") as config:
            yaml.dump(
                {
                    "api_id": 123456,
                    "api_hash": "wahgi231kmdma91",
                    "session_name": "test",
                },
                config,
            )
        accounts = ["1004347112", "1196000400", "1415098098", "1446651076"]
        # fake account list
        with list_file.open("w") as account_list:
            for line in accounts:
                account_list.write(line + "\n")

        # run command
        result = runner.invoke(
            cli,
            "group init\
             --read_file account_list.csv\
             --start_date 2022-01-01 my_little_account_list",
        )

        assert result.exit_code == 0  # indicating success?
        assert r_folder.exists()  # is the folder created?
        assert r_file.exists()  # does the group conf exists?

        with r_file.open("r") as file:
            res = yaml.full_load(file)
            assert isinstance(res, Group)
            for member in res.members:
                assert member in accounts


def test_search(runner: CliRunner):
    """Should get search results for specified terms"""

    result = runner.invoke(cli, ["search", "term"])

    assert result.exit_code == 0


patcher.stop()
