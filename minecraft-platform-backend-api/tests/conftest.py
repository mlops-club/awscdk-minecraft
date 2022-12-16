"""Reusable fixtures for the tests."""
import os  # noqa: D100 C0114
import sys
from pathlib import Path

import pytest
from aws_cdk import Environment

THIS_DIR = Path(__file__).parent
sys.path.append(str(THIS_DIR))


@pytest.fixture(scope="module")
def dev_env():  # noqa: D103
    return Environment(account=os.environ["AWS_ACCOUNT_ID"], region=os.environ["AWS_REGION"])


pytest_plugins = ["fixtures.settings", "fixtures.state_machine"]
