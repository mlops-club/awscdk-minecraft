"""Reusable fixtures for the tests."""
import os  # noqa: D100 C0114

import pytest
from aws_cdk import Environment


@pytest.fixture(scope="module")
def dev_env():  # noqa: D103
    return Environment(account=os.environ["AWS_ACCOUNT_ID"], region=os.environ["AWS_REGION"])
