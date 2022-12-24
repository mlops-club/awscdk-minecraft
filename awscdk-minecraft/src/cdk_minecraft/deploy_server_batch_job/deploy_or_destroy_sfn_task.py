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
