import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run_api", action="store_true", default=False, help="run tests against the Telegram API"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "api: mark test as running against the Telegram API")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run_api"):
        # --run_api given in cli: do not skip slow tests
        return
    skip_api = pytest.mark.skip(reason="need --run_api option to run")
    for item in items:
        if "api" in item.keywords:
            item.add_marker(skip_api)
