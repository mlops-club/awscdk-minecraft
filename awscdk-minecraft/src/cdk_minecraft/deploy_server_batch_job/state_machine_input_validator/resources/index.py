from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Dict, Literal, Optional

from pydantic import BaseModel, validator


def handler(event: Dict[str, str], context):
    """Validate the ``event`` state machine input object."""
    ProvisionMinecraftServerStateMachineInput(**event)


class ProvisionMinecraftServerStateMachineInput(BaseModel):
    """

    Attributes:
        command: When the command is "deploy", a server will be provisioned or a no-op will occur if the server is already up.

        destroy_at_utc_timestamp: When the command is destroy, "destroy_at_utc_timestamp" must be set to a timestamp in the future.
            This will be provided as a UTC ISO timestamp string. The server will be destroyed at that time.
    """

    command: Literal["deploy", "destroy"]
    """
    When the command is "deploy", a server will be provisioned or a no-op will occur if the server is already up.

    When the command is destroy, "destroy_at_utc_timestamp" must be set to a timestamp in the future.
    The server will be destroyed at that time.
    """

    destroy_at_utc_timestamp: Optional[datetime] = None

    # validator that parses destroy_at_utc_timestamp to a datetime object if a string is provided
    @validator("destroy_at_utc_timestamp", pre=True, always=True)
    def parse_destroy_at_utc_timestamp(  # pylint: disable=no-self-argument
        cls, destroy_at_utc_timestamp: Optional[str] = None, values: Dict[str, str] = None
    ):
        """Raise a validation error if command is destroy, but destroy_at_utc_timestamp is a valid ISO formatted timestamp string."""
        if values["command"] == "destroy":

            if not destroy_at_utc_timestamp:
                raise ValueError("'destroy_at_utc_timestamp' must be set when 'command' is destroy")

            destroy_at_utc_timestamp = try_parse_datetime_from_iso_string(iso_string=destroy_at_utc_timestamp)
            assert_datetime_is_in_future(timestamp=destroy_at_utc_timestamp)
            return destroy_at_utc_timestamp

        return destroy_at_utc_timestamp


def try_parse_datetime_from_iso_string(iso_string: str) -> datetime:
    try:
        return datetime.fromisoformat(iso_string)
    except ValueError as err:
        raise ValueError(
            f"destroy_at_utc_timestamp must be set to an ISO formatted timstamp string when command is destroy. \n{str(err)}"
        )


def assert_datetime_is_in_future(timestamp: datetime):
    utc_now: datetime = datetime.now(tz=timezone.utc)
    utc_timestamp: datetime = convert_zoned_datetime_to_utc_datetime(zoned_datetime=timestamp)
    if utc_timestamp < utc_now:
        current_iso_time: str = utc_now.isoformat()
        timestamp_as_iso_string: str = timestamp.isoformat()
        raise ValueError(
            f"'timestamp' must be set to a timestamp in the future. Now is {current_iso_time}. Got: {timestamp_as_iso_string}"
        )


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
    handler(event, None)


def raise_value_error_when_command_is_destroy_but_destroy_at_utc_timestamp_is_not_a_valid_iso_formatted_timestamp_string():
    event = {
        "command": "destroy",
        "destroy_at_utc_timestamp": "2021-04-12T23:59:59.999999Z",
    }
    handler(event, None)


def raise_value_error_when_command_is_destroy_but_destroy_at_utc_timestamp_is_not_set():
    event = {
        "command": "destroy",
    }
    handler(event, None)


def run_destroy_command_with_a_valid_utc_timestamp_in_the_future():
    event = {
        "command": "destroy",
        "destroy_at_utc_timestamp": "2030-04-12T23:59:59.999999+00:00",
    }
    handler(event, None)


def run_deploy_command():
    event = {
        "command": "deploy",
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

    # expect error when command is destroy, but destroy_at_utc_timestamp is in the past
    with should_raise_value_error():
        raise_value_error_when_command_is_destroy_but_destroy_at_utc_timestamp_is_in_the_past()

    # # expect error when command is destroy, but destroy_at_utc_timestamp is not a valid ISO formatted timestamp string
    with should_raise_value_error():
        raise_value_error_when_command_is_destroy_but_destroy_at_utc_timestamp_is_not_a_valid_iso_formatted_timestamp_string()

    # expect error when command is destroy, but destroy_at_utc_timestamp is not set
    with should_raise_value_error():
        raise_value_error_when_command_is_destroy_but_destroy_at_utc_timestamp_is_not_set()

    # expect success when command is destroy, and destroy_at_utc_timestamp is set to a valid ISO formatted timestamp string in the future
    run_destroy_command_with_a_valid_utc_timestamp_in_the_future()

    # expect success when command is deploy, and destroy_at_utc_timestamp is not set
    run_deploy_command()
