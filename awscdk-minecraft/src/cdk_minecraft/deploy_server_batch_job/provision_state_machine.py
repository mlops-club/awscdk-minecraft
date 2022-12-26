"""AWS Step Function (State Machine) that deploys or destroys the Minecraft server."""

from pathlib import Path

from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks
from cdk_minecraft.deploy_server_batch_job.state_machine_input_validator.state_machine_input_validator_lambda import (
    make_lambda_that_validates_input_of_the_provision_server_state_machine,
)
from constructs import Construct

THIS_DIR = Path(__file__).parent


def create__input_validation_lambda(scope: Construct, id_prefix: str) -> sfn_tasks.LambdaInvoke:
    """Return a task that validates the execution input of the provision server state machine."""
    validate_input_fn: lambda_.Function = (
        make_lambda_that_validates_input_of_the_provision_server_state_machine(scope=scope, id_prefix=id_prefix)
    )

    # return a task that passes the entire input as the event in the validator lambda function
    return sfn_tasks.LambdaInvoke(
        scope=scope,
        id=f"{id_prefix}Validate Input",
        lambda_function=validate_input_fn,
        # payload=sfn.TaskInput.from_json_path_at("$"),
        input_path="$",
        output_path="$",
        result_path="$",
        payload_response_only=True,
    )


class ProvisionMinecraftServerStateMachine(Construct):
    """
    Class for the State Machine to deploy our Minecraft server.

    The State Machine will be responsible for starting and stopping the server.

    :param scope: The parent construct.
    :param construct_id: The name of the construct.
    :param job_queue_arn: The ARN of the AWS Batch Job Queue.
    :param deploy_mc_server_job_definition_arn: The ARN of the AWS Batch Job Definition for the CDK Deploy or Destroy Job.
    :param ensure_unique_id_names: Whether to prefix the name of the construct with the name of the construct.

    :ivar state_machine: The AWS Step Function State Machine.
    :ivar namer: A function that prefixes the name of the construct with the name of the construct.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        job_queue_arn: str,
        deploy_mc_server_job_definition_arn: str,
        ensure_unique_id_names: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.namer = lambda name: f"{construct_id}-{name}" if ensure_unique_id_names else name
        self.ensure_unique_id_names = ensure_unique_id_names

        submit_cdk_deploy_batch_job: sfn_tasks.BatchSubmitJob = self.create__deploy__submit_batch_job_state(
            state_machine_arn=deploy_mc_server_job_definition_arn,
            job_queue_arn=job_queue_arn,
        )

        validate_execution_input: sfn_tasks.LambdaInvoke = create__input_validation_lambda(
            scope=self, id_prefix=construct_id if ensure_unique_id_names else ""
        )

        self.state_machine = sfn.StateMachine(
            scope=self,
            id=self.namer("StateMachine"),
            definition=validate_execution_input.next(submit_cdk_deploy_batch_job),
            # logs=sfn.LogOptions(),
            role=None,
        )

    # method for submit_cdk_deploy_batch_job
    def create__deploy__submit_batch_job_state(
        self, state_machine_arn: str, job_queue_arn: str
    ) -> sfn_tasks.BatchSubmitJob:
        return create__deploy__submit_batch_job_state(
            scope=self,
            id_prefix=self.node.id if self.ensure_unique_id_names else "",
            job_queue_arn=job_queue_arn,
            deploy_mc_server_job_definition_arn=state_machine_arn,
        )


def create__deploy__submit_batch_job_state(
    scope: Construct,
    id_prefix: str,
    job_queue_arn: str,
    deploy_mc_server_job_definition_arn: str,
) -> sfn_tasks.BatchSubmitJob:
    """
    Create the AWS Step Function State that submits the AWS Batch Job to deploy the Minecraft server.

    :param scope: The parent construct.
    :param id_prefix: The prefix for the ID of the AWS Step Function State.
    :param job_queue_arn: The ARN of the AWS Batch Job Queue.
    :param deploy_mc_server_job_definition_arn: The ARN of the AWS Batch Job Definition for the CDK Deploy Job.

    :return: The AWS Step Function State that submits the AWS Batch Job to deploy the Minecraft server.
    """
    return sfn_tasks.BatchSubmitJob(
        scope=scope,
        id=f"Deploy Server {id_prefix}".strip(),
        job_name=f"{id_prefix}DeployMinecraftServer",
        container_overrides=sfn_tasks.BatchContainerOverrides(
            environment=None,
            command=["cdk", "deploy", "--app", "'python3 /app/app.py'", "--require-approval=never"],
        ),
        job_queue_arn=job_queue_arn,
        job_definition_arn=deploy_mc_server_job_definition_arn,
    )
