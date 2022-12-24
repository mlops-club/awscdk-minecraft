"""AWS Step Function (State Machine) that deploys or destroys the Minecraft server."""
from pathlib import Path
from typing import Literal, TypedDict
from typing_extensions import NotRequired

from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks
from cdk_minecraft.deploy_server_batch_job.state_machine_input_validator.state_machine_input_validator_lambda import (
    make_lambda_that_validates_input_of_the_provision_server_state_machine,
)
from cdk_minecraft.

from constructs import Construct

THIS_DIR = Path(__file__).parent


class DeprovisionServerSfnInput(TypedDict):
    """State machine input for the ``DeprovisionMinecraftServerStateMachine``."""

    wait_n_seconds_before_destroy: NotRequired[int]


class DeprovisionMinecraftServerStateMachine(Construct):
    """

    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        job_queue_arn: str,
        deploy_or_destroy_mc_server_job_definition_arn: str,
        ensure_unique_id_names: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.namer = lambda name: f"{construct_id}-{name}" if ensure_unique_id_names else name
        self.ensure_unique_id_names = ensure_unique_id_names

        submit_cdk_destroy_batch_job: sfn_tasks.BatchSubmitJob = self.create__destroy__submit_batch_job_state(
            state_machine_arn=deploy_or_destroy_mc_server_job_definition_arn,
            job_queue_arn=job_queue_arn,
        )

        
        n_seconds_greater_than_30: sfn.Condition = sfn.Condition.number_greater_than_equals_json_path(
            value=30, json_path="$.wait_n_seconds_before_destroy"
        )
        
        # destroy the server now if $.destroy_at_utc_timestamp is NOT present, otherwise wait until the timestamp
        destroy_server_now_or_at_timestamp = (
            sfn.Choice(
                self,
                id=self.namer("Destroy Server Now or at Timestamp"),
            )
            .when(
                condition=sfn.Condition.is_present("$.wait_n_seconds_before_destroy"),
                next=sfn.Wait(
                    self,
                    id=self.namer("Wait N seconds"),
                    time=sfn.WaitTime.seconds_path("$.wait_n_seconds_before_destroy"),
                ).next(submit_cdk_destroy_batch_job),
            )
            .when(
                condition=sfn.Condition.is_not_present("$.wait_n_seconds_before_destroy"),
                next=submit_cdk_destroy_batch_job,
            )
        )


        self.state_machine = sfn.StateMachine(
            scope=self,
            id=self.namer("StateMachine"),
            definition=validate_execution_input.next(deploy_or_destroy_server),
            # logs=sfn.LogOptions(),
            role=None,
        )

    def create__destroy__submit_batch_job_state(
        self, state_machine_arn: str, job_queue_arn: str
    ) -> sfn_tasks.BatchSubmitJob:
        return create__deploy_or_destroy__submit_batch_job_state(
            scope=self,
            command="destroy",
            id_prefix=self.node.id if self.ensure_unique_id_names else "",
            job_queue_arn=job_queue_arn,
            deploy_or_destroy_mc_server_job_definition_arn=state_machine_arn,
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
