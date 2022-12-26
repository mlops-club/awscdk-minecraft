import re
from contextlib import contextmanager
from pprint import pprint
from typing import Dict, Optional

from pydantic import BaseModel, validator


def handler(event: Dict[str, str], context) -> Dict[str, str]:
    """Validate the ``event`` state machine input object."""
    print("event: ")
    pprint(event)
    ProvisionMinecraftServerStateMachineInput(**event)
    return event


class ProvisionMinecraftServerStateMachineInput(BaseModel):
    """Ensures that the state machine input object is valid.
    Attributes:
        version: The version of Minecraft to provision. Must be formatted as 'x.y.z' (integers, with 'z' optional).
    """

    version: Optional[str] = None

    # validator that parses version to a datetime object if a string is provided
    @validator("version", pre=True, always=False)
    def validate_version(cls, version: str):
        """Raise a validation error if version is not formatted as 'x.y.z' (integers, with 'z' optional)."""
        assert_that_version_is_formatted_correctly(version=version)
        return version


def assert_that_version_is_formatted_correctly(version: str) -> bool:
    """Return True if the version is formatted as 'x.y.z' (integers, with 'z' optional)."""
    semver_pattern = r"^\d+\.\d+(\.\d+)?$"
    is_valid_semver = bool(re.match(semver_pattern, version))
    if not is_valid_semver:
        raise ValueError(f"version must be formatted as (integers) 'x.y.z' or 'x.y'. Got: {version}")


#################
# --- Tests --- #
#################


def run_with_empty_event():
    event = {}
    handler(event, None)


def run_with_full_version():
    event = {
        "version": "1.8.8",
    }
    handler(event, None)


def run_with_major_version():
    event = {
        "version": "1.19",
    }
    handler(event, None)


def raise_value_error_when_version_is_integer():
    event = {
        "version": "1",
    }
    handler(event, None)


def raise_value_error_when_version_is_misformatted():
    event = {
        "version": "1.",
    }
    handler(event, None)


@contextmanager
def should_raise_value_error():
    try:
        yield
    except ValueError:
        pass
    else:
        raise AssertionError("ValueError was not raised")


# run a few tests to make sure the validation works as expected
if __name__ == "__main__":

    # expect error if version misformatted
    with should_raise_value_error():
        raise_value_error_when_version_is_misformatted()

    with should_raise_value_error():
        raise_value_error_when_version_is_integer()

    # expect success when version is not set
    run_with_empty_event()

    # expect success when version is valid
    run_with_full_version()

    # expect success when version is valid but 'z' is not set (i.e., 'x.y')
    run_with_major_version()
