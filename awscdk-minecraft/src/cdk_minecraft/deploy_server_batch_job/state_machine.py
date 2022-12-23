"""AWS Step Function (State Machine) that deploys or destroys the Minecraft server."""
from pathlib import Path
from typing import Literal

from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks
from cdk_minecraft.deploy_server_batch_job.state_machine_input_validator.state_machine_input_validator_lambda import (
    make_lambda_that_validates_input_of_the_provision_server_state_machine,
)
from constructs import Construct

THIS_DIR = Path(__file__).parent


class ProvisionMinecraftServerStateMachine(Construct):
    """
    Class for the State Machine to deploy our Minecraft server.

    The State Machine will be responsible for starting and stopping the server.

    Parameters
    ----------
    scope : Construct
        The parent construct.
    construct_id : str
        The name of the construct.
    job_queue_arn : str
        The ARN of the AWS Batch Job Queue.
    deploy_or_destroy_mc_server_job_definition_arn : str
        The ARN of the AWS Batch Job Definition for the CDK Deploy or Destroy Job.

    Attributes
    ----------
    state_machine : sfn.StateMachine
        The AWS Step Function State Machine.
    namer : Callable[[str], str]
        A function that prefixes the name of the construct with the name of the construct.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        job_queue_arn: str,
        deploy_or_destroy_mc_server_job_definition_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.namer = lambda name: f"{construct_id}-{name}"

        submit_cdk_deploy_batch_job: sfn_tasks.BatchSubmitJob = (
            create__deploy_or_destroy__submit_batch_job_state(
                scope=self,
                command="deploy",
                id_prefix=construct_id,
                job_queue_arn=job_queue_arn,
                deploy_or_destroy_mc_server_job_definition_arn=deploy_or_destroy_mc_server_job_definition_arn,
            )
        )

        submit_cdk_destroy_batch_job: sfn_tasks.BatchSubmitJob = (
            create__deploy_or_destroy__submit_batch_job_state(
                scope=self,
                command="destroy",
                id_prefix=construct_id,
                job_queue_arn=job_queue_arn,
                deploy_or_destroy_mc_server_job_definition_arn=deploy_or_destroy_mc_server_job_definition_arn,
            )
        )

        state_machine = create__validate_input__state(scope=self, id_prefix=construct_id).next(
            sfn.Choice(
                self,
                id=self.namer("ChooseCdkDeployOrDestroy"),
            )
            .when(
                condition=sfn.Condition.string_equals("$.command", "deploy"), next=submit_cdk_deploy_batch_job
            )
            .when(
                condition=sfn.Condition.string_equals("$.command", "destroy"),
                next=submit_cdk_destroy_batch_job,
            )
        )

        self.state_machine = sfn.StateMachine(
            scope=self,
            id=self.namer("StateMachine"),
            definition=state_machine,
            # logs=sfn.LogOptions(),
            role=None,
        )


def create__deploy_or_destroy__submit_batch_job_state(
    scope: Construct,
    id_prefix: str,
    command: Literal["deploy", "destroy"],
    job_queue_arn: str,
    deploy_or_destroy_mc_server_job_definition_arn: str,
) -> sfn_tasks.BatchSubmitJob:
    """Create the AWS Step Function State that submits the AWS Batch Job to deploy or destroy the Minecraft server.

    Parameters
    ----------
    scope : Construct
        The parent construct.
    id_prefix : str
        The prefix for the ID of the AWS Step Function State.
    command : Literal["deploy", "destroy"]
        The command to run. Must be one of "deploy" or "destroy".
    job_queue_arn : str
        The ARN of the AWS Batch Job Queue.
    deploy_or_destroy_mc_server_job_definition_arn : str
        The ARN of the AWS Batch Job Definition for the CDK Deploy or Destroy Job.

    Returns
    -------
    sfn_tasks.BatchSubmitJob
        The AWS Step Function State that submits the AWS Batch Job to deploy or destroy the Minecraft server.
    """
    if command == "deploy":
        return sfn_tasks.BatchSubmitJob(
            scope=scope,
            id=f"{id_prefix}CdkDeployMcServerBatchJob",
            job_name=f"{id_prefix}DeployMinecraftServer",
            container_overrides=sfn_tasks.BatchContainerOverrides(
                environment=None,
                command=["cdk", "deploy", "--app", "'python3 /app/app.py'", "--require-approval=never"],
            ),
            job_queue_arn=job_queue_arn,
            job_definition_arn=deploy_or_destroy_mc_server_job_definition_arn,
        )

    if command == "destroy":
        return sfn_tasks.BatchSubmitJob(
            scope=scope,
            id=f"{id_prefix}CdkDestroyMcServerBatchJob",
            job_name=f"{id_prefix}DestroyMinecraftServer",
            container_overrides=sfn_tasks.BatchContainerOverrides(
                environment=None,
                command=["cdk", "destroy", "--app", "'python3 /app/app.py'", "--force"],
            ),
            job_queue_arn=job_queue_arn,
            job_definition_arn=deploy_or_destroy_mc_server_job_definition_arn,
        )

    raise ValueError("Invalid command. ``command`` must be one of 'destroy' or 'deploy'")


def create__validate_input__state(scope: Construct, id_prefix: str) -> sfn_tasks.LambdaInvoke:
    """Return a task that validates the execution input of the provision server state machine."""

    validate_input_fn: lambda_.Function = (
        make_lambda_that_validates_input_of_the_provision_server_state_machine(scope=scope, id_prefix=id_prefix)
    )

    # return a task that passes the entire input as the event in the validator lambda function
    return sfn_tasks.LambdaInvoke(
        scope=scope,
        id=f"{id_prefix}ValidateInput",
        lambda_function=validate_input_fn,
        # payload=sfn.TaskInput.from_json_path_at("$"),
        input_path="$",
        output_path="$",
        result_path="$",
        payload_response_only=True,
    )
