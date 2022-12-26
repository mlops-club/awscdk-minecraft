"""AWS Step Function (State Machine) that deploys or destroys the Minecraft server."""
from pathlib import Path
from typing import TypedDict

from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks
from constructs import Construct
from typing_extensions import NotRequired

THIS_DIR = Path(__file__).parent

MIN_NUMBER_OF_MINUTES_ALLOWED_FOR_SERVER_UPTIME = 30
MAX_NUMBER_OF_MINUTES_ALLOWED_FOR_SERVER_UPTIME = 60 * 3


def minutes_to_seconds(minutes: int) -> int:
    """Convert minutes to seconds."""

    return minutes * 60


class DeprovisionServerSfnInput(TypedDict):
    """State machine input for the ``DeprovisionMinecraftServerStateMachine``."""

    wait_n_seconds_before_destroy: NotRequired[int]


class DeprovisionMinecraftServerStateMachine(Construct):
    """

    ```
    start
        |
    if present        if not present
        |                  |-------------> destroy right now
    validate
        |
    assert n_seconds >= minimum (30 minutes)  -------> Fail
        |
    wait n seconds
        |--------------------------------> destroy right now
    ```
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        job_queue_arn: str,
        destroy_mc_server_job_definition_arn: str,
        ensure_unique_id_names: bool = False,
        min_number_of_minutes_allowed_for_server_uptime: int = MIN_NUMBER_OF_MINUTES_ALLOWED_FOR_SERVER_UPTIME,
        max_number_of_minutes_allowed_for_server_uptime: int = MAX_NUMBER_OF_MINUTES_ALLOWED_FOR_SERVER_UPTIME,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.namer = lambda name: f"{construct_id}-{name}" if ensure_unique_id_names else name
        self.ensure_unique_id_names = ensure_unique_id_names

        submit_cdk_destroy_batch_job: sfn_tasks.BatchSubmitJob = self.create__destroy__submit_batch_job_state(
            state_machine_arn=destroy_mc_server_job_definition_arn,
            job_queue_arn=job_queue_arn,
        )

        self.min_number_of_minutes_allowed_for_server_uptime: int = (
            min_number_of_minutes_allowed_for_server_uptime
        )
        self.max_number_of_minutes_allowed_for_server_uptime: int = (
            max_number_of_minutes_allowed_for_server_uptime
        )

        wait_time__gr_or_eq__min_allowed_uptime_secs = sfn.Condition.number_greater_than_equals(
            variable="$.wait_n_seconds_before_destroy",
            value=minutes_to_seconds(min_number_of_minutes_allowed_for_server_uptime),
        )

        wait_time__le_or_eq__max_allowed_uptime_secs = sfn.Condition.number_less_than_equals(
            variable="$.wait_n_seconds_before_destroy",
            value=minutes_to_seconds(max_number_of_minutes_allowed_for_server_uptime),
        )

        wait_time_is_in_valid_range: sfn.Condition = sfn.Condition.and_(
            wait_time__gr_or_eq__min_allowed_uptime_secs,
            wait_time__le_or_eq__max_allowed_uptime_secs,
        )

        wait_n_seconds_before_destroy = sfn.Wait(
            self,
            id="Wait N seconds",
            time=sfn.WaitTime.seconds_path("$.wait_n_seconds_before_destroy"),
        )

        failure__wait_time_is_too_short = sfn.Fail(
            self,
            id=f"Fail: invalid wait time",
            cause=f"Wait time is too short or too long. The server must be up {min_number_of_minutes_allowed_for_server_uptime} <= time <= {max_number_of_minutes_allowed_for_server_uptime} minutes.",
        )

        wait_and_then_destroy_server = (
            sfn.Choice(self, "Is wait time in valid range?")
            .when(
                condition=wait_time_is_in_valid_range,
                next=wait_n_seconds_before_destroy.next(submit_cdk_destroy_batch_job),
            )
            .otherwise(failure__wait_time_is_too_short)
        )

        is_wait_time_present = sfn.Condition.is_present(variable="$.wait_n_seconds_before_destroy")

        # Entrypoint for the DAG
        destroy_server = (
            sfn.Choice(self, id="Is wait time present?")
            .when(
                condition=is_wait_time_present,
                next=wait_and_then_destroy_server,
            )
            .otherwise(
                submit_cdk_destroy_batch_job,
            )
        )

        self.state_machine = sfn.StateMachine(
            scope=self,
            id=self.namer("StateMachine"),
            definition=destroy_server,
            role=None,
        )

    def create__destroy__submit_batch_job_state(
        self, state_machine_arn: str, job_queue_arn: str
    ) -> sfn_tasks.BatchSubmitJob:
        return create__destroy__submit_batch_job_state(
            scope=self,
            id_prefix=self.node.id if self.ensure_unique_id_names else "",
            job_queue_arn=job_queue_arn,
            destroy_mc_server_job_definition_arn=state_machine_arn,
        )


def create__destroy__submit_batch_job_state(
    scope: Construct,
    id_prefix: str,
    job_queue_arn: str,
    destroy_mc_server_job_definition_arn: str,
) -> sfn_tasks.BatchSubmitJob:
    """Create the AWS Step Function State that submits the AWS Batch Job to deploy the Minecraft server.

    :param scope: The scope of the construct.
    :param id_prefix: The prefix to use for the ID of the construct.
    :param job_queue_arn: The ARN of the AWS Batch Job Queue to submit the job to.
    :param deploy_mc_server_job_definition_arn: The ARN of the AWS Batch Job Definition to use for the job.

    :return: The AWS Step Function State that submits the AWS Batch Job to deploy the Minecraft server.
    """
    return sfn_tasks.BatchSubmitJob(
        scope=scope,
        id=f"{id_prefix}Destroy Server",
        job_name=f"{id_prefix}DestroyMinecraftServer",
        container_overrides=sfn_tasks.BatchContainerOverrides(
            environment=None,
            command=["cdk", "destroy", "--app", "'python3 /app/app.py'", "--force"],
        ),
        job_queue_arn=job_queue_arn,
        job_definition_arn=destroy_mc_server_job_definition_arn,
    )


# def create__validate_input__state(scope: Construct, id_prefix: str) -> sfn_tasks.LambdaInvoke:
#     """Return a task that validates the execution input of the provision server state machine."""
#     validate_input_fn: lambda_.Function = (
#         make_lambda_that_validates_input_of_the_provision_server_state_machine(scope=scope, id_prefix=id_prefix)
#     )

#     # return a task that passes the entire input as the event in the validator lambda function
#     return sfn_tasks.LambdaInvoke(
#         scope=scope,
#         id=f"{id_prefix}ValidateInput",
#         lambda_function=validate_input_fn,
#         # payload=sfn.TaskInput.from_json_path_at("$"),
#         input_path="$",
#         output_path="$",
#         result_path="$",
#         payload_response_only=True,
#     )
#     )
