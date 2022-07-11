import pytest
from click.testing import CliRunner
from tegracli.main import cli

@pytest.fixture
def runner():
    """ Fixture for click.CliRunner
    """
    return CliRunner()

def test_cli(runner: CliRunner):
    """ Should show help if no args present
    """
    result = runner.invoke(cli, [''])
    
    assert result.exit_code == 2

def test_get(runner: CliRunner):
    """ Should get results for specified channels
    """

    result = runner.invoke(cli, ['get', 'channel'])

    assert result.exit_code == 0

def test_search(runner: CliRunner):
    """ Should get search results for specified terms
    """

    result = runner.invoke(cli, ['search', 'term'])

    assert result.exit_code == 0
