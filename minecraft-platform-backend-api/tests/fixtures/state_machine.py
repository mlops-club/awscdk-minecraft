"""Mocked state machine for tests."""

import json

import boto3
import pytest
from moto import mock_stepfunctions
from mypy_boto3_stepfunctions import SFNClient

STATE_MACHINE_DEFINITION = {
    "StartAt": "awscdk-minecraftProvisionMcStateMachine-ChooseCdkDeployOrDestroy",
    "States": {
        "awscdk-minecraftProvisionMcStateMachine-ChooseCdkDeployOrDestroy": {
            "Type": "Choice",
            "Choices": [
                {
                    "Variable": "$.command",
                    "StringEquals": "deploy",
                    "Next": "awscdk-minecraftProvisionMcStateMachineCdkDeployMcServerBatchJob",
                },
                {
                    "Variable": "$.command",
                    "StringEquals": "destroy",
                    "Next": "awscdk-minecraftProvisionMcStateMachineCdkDestroyMcServerBatchJob",
                },
            ],
        },
        "awscdk-minecraftProvisionMcStateMachineCdkDeployMcServerBatchJob": {
            "End": True,
            "Type": "Task",
            "Resource": "arn:aws:states:::batch:submitJob.sync",
            "Parameters": {
                "JobDefinition": "arn:aws:batch:us-west-2:630013828440:job-definition/McDeployJobDefinitionCd-8ea9140b7faf087:1",
                "JobName": "awscdk-minecraftProvisionMcStateMachineDeployMinecraftServer",
                "JobQueue": "arn:aws:batch:us-west-2:630013828440:job-queue/CdkDockerBatchEnvCdkDock-KbAffuL47Ws4y1Jt",
                "ContainerOverrides": {
                    "Command": ["cdk", "deploy", "--app", "'python3 /app/app.py'", "--require-approval=never"]
                },
            },
        },
        "awscdk-minecraftProvisionMcStateMachineCdkDestroyMcServerBatchJob": {
            "End": True,
            "Type": "Task",
            "Resource": "arn:aws:states:::batch:submitJob.sync",
            "Parameters": {
                "JobDefinition": "arn:aws:batch:us-west-2:630013828440:job-definition/McDeployJobDefinitionCd-8ea9140b7faf087:1",
                "JobName": "awscdk-minecraftProvisionMcStateMachineDestroyMinecraftServer",
                "JobQueue": "arn:aws:batch:us-west-2:630013828440:job-queue/CdkDockerBatchEnvCdkDock-KbAffuL47Ws4y1Jt",
                "ContainerOverrides": {
                    "Command": ["cdk", "destroy", "--app", "'python3 /app/app.py'", "--force"]
                },
            },
        },
    },
}


@pytest.fixture
def state_machine_arn() -> str:
    """Create a step functions state machine with boto; return its ARN."""
    with mock_stepfunctions():
        sfn_client: SFNClient = boto3.client("stepfunctions")
        create_state_machine: dict = sfn_client.create_state_machine(
            name="provision-minecraft-server",
            definition=json.dumps(STATE_MACHINE_DEFINITION),
            roleArn="arn:aws:iam::123456789012:role/service-role/StepFunctions-ExecutionRole-us-east-1",
        )

        yield create_state_machine["stateMachineArn"]
