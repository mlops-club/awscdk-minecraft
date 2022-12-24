from contextlib import contextmanager
from datetime import datetime, timezone
from pprint import pprint
from typing import Dict, Literal, Optional

from pydantic import BaseModel, validator


def destroy_handler(event: Dict[str, str], context) -> Dict[str, str]:
    """Validate the ``event`` state machine input object."""
    print("event: ")
    pprint(event)
    DeProvisionMinecraftServerStateMachineInput(**event)
    return event


def deploy_handler(event: Dict[str, str], context) -> Dict[str, str]:
    """Validate the ``event`` state machine input object."""
    print("event: ")
    pprint(event)
    ProvisionMinecraftServerStateMachineInput(**event)
    return event

def handler(event: Dict[str, str], conte)

class ProvisionMinecraftServerStateMachineInput(BaseModel):
    """

    Attributes:
        version: The version of Minecraft to provision. Must be formatted as 'x.y.z' (integers, with 'z' optional).
    """

    version: str

    # validator that parses version to a datetime object if a string is provided
    @validator(
        "version", pre=True, always=True
    )  # TODO: do we need always=True here? will the field "version" fall back to an env var if not provided?
    def validate_version(cls, version: str):
        """Raise a validation error if version is not formatted as 'x.y.z' (integers, with 'z' optional)."""
        assert_that_version_is_formatted_correctly(version=version)
        return version


class DeProvisionMinecraftServerStateMachineInput(BaseModel):
    """

    Attributes:
        destroy_at_utc_timestamp: When the command is destroy, "destroy_at_utc_timestamp" must be set to a timestamp in the future.
            This will be provided as a UTC ISO timestamp string. The server will be destroyed at that time.
    """

    destroy_at_utc_timestamp: Optional[datetime] = None

    # validator that parses destroy_at_utc_timestamp to a datetime object if a string is provided
    @validator("destroy_at_utc_timestamp", pre=True, always=True)
    def parse_destroy_at_utc_timestamp(  # pylint: disable=no-self-argument
        cls,
        destroy_at_utc_timestamp: Optional[str] = None,
    ):
        destroy_at_utc_timestamp = try_parse_datetime_from_iso_string(iso_string=destroy_at_utc_timestamp)
        assert_datetime_is_in_future(timestamp=destroy_at_utc_timestamp)
        return destroy_at_utc_timestamp


def try_parse_datetime_from_iso_string(iso_string: str) -> datetime:
    try:
        return datetime.fromisoformat(iso_string)
    except ValueError as err:
        raise ValueError(
            f"destroy_at_utc_timestamp must be set to an ISO formatted timstamp string when command is destroy. \n{str(err)}"
        ) from err


def assert_datetime_is_in_future(timestamp: datetime):
    utc_now: datetime = datetime.now(tz=timezone.utc)
    utc_timestamp: datetime = convert_zoned_datetime_to_utc_datetime(zoned_datetime=timestamp)
    if utc_timestamp < utc_now:
        current_iso_time: str = utc_now.isoformat()
        timestamp_as_iso_string: str = timestamp.isoformat()
        raise ValueError(
            f"'timestamp' must be set to a timestamp in the future. Now is {current_iso_time}. Got: {timestamp_as_iso_string}"
        )


def assert_that_version_is_formatted_correctly(version: str):
    version_parts = version.split(".")
    error_msg = f"version must be formatted as (integers) 'x.y.z' or 'x.y'. Got: {version}"
    if len(version_parts) != 3:
        raise ValueError(error_msg)
    if len(version_parts) == 1:
        raise ValueError(error_msg)
    for part in version_parts:
        try:
            int(part)
        except ValueError as err:
            raise ValueError(error_msg) from err


def convert_zoned_datetime_to_utc_datetime(zoned_datetime: datetime) -> datetime:
    return zoned_datetime.astimezone(tz=timezone.utc)


#################
# --- Tests --- #
#################


def raise_value_error_when_command_is_destroy_but_destroy_at_utc_timestamp_is_in_the_past():
    event = {
        "command": "destroy",
        "destroy_at_utc_timestamp": "2021-04-12T23:59:59.999999",
    }
    destroy_handler(event, None)


def raise_value_error_when_command_is_destroy_but_destroy_at_utc_timestamp_is_not_a_valid_iso_formatted_timestamp_string():
    event = {
        "command": "destroy",
        "destroy_at_utc_timestamp": "2021-04-12T23:59:59.999999Z",
    }
    destroy_handler(event, None)


def raise_value_error_when_command_is_destroy_but_destroy_at_utc_timestamp_is_not_set():
    event = {
        "command": "destroy",
    }
    destroy_handler(event, None)


def run_destroy_command_with_a_valid_utc_timestamp_in_the_future():
    event = {
        "command": "destroy",
        "destroy_at_utc_timestamp": "2030-04-12T23:59:59.999999+00:00",
    }
    destroy_handler(event, None)


def run_deploy_command():
    event = {
        "command": "deploy",
    }
    deploy_handler(event, None)


def run_deploy_command_with_full_version():
    event = {
        "command": "deploy",
        "version": "1.8.8",
    }
    deploy_handler(event, None)


def run_deploy_command_with_major_version():
    event = {
        "command": "deploy",
        "version": "1.19",
    }
    deploy_handler(event, None)


def raise_value_error_when_command_is_deploy_but_version_is_misformatted():
    event = {
        "command": "deploy",
        "version": "1",
    }
    deploy_handler(event, None)


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

    # expect error when command is destroy, but destroy_at_utc_timestamp is in the past
    with should_raise_value_error():
        raise_value_error_when_command_is_destroy_but_destroy_at_utc_timestamp_is_in_the_past()

    # expect error when command is destroy, but destroy_at_utc_timestamp is not a valid ISO formatted timestamp string
    with should_raise_value_error():
        raise_value_error_when_command_is_destroy_but_destroy_at_utc_timestamp_is_not_a_valid_iso_formatted_timestamp_string()

    # expect error if version misformatted
    with should_raise_value_error():
        raise_value_error_when_command_is_deploy_but_version_is_misformatted()
    
    # expect success when command is destroy, and destroy_at_utc_timestamp is set to a valid ISO formatted timestamp string in the future
    run_destroy_command_with_a_valid_utc_timestamp_in_the_future()

    # expect success when command is deploy, and version is not set
    run_deploy_command()

    # expect success when command is deploy, and version is valid
    run_deploy_command_with_full_version()

    # expect success when command is deploy and version is valid but 'z' is not set
    run_deploy_command_with_major_version()
