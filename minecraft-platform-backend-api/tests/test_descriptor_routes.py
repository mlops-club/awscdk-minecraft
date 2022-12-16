from pydoc import describe

import boto3
from moto import mock_stepfunctions
import pytest
from mypy_boto3_stepfunctions import SFNClient
import json
from fastapi.testclient import TestClient
from fastapi import Response
from minecraft_paas_api.main import create_app
from starlette.status import HTTP_200_OK
from datetime import datetime

import os
os.environ["AWS_REGION"] = "us-west-2"

STATE_MACHINE_DEFINITION = {
  "StartAt": "awscdk-minecraftProvisionMcStateMachine-ChooseCdkDeployOrDestroy",
  "States": {
    "awscdk-minecraftProvisionMcStateMachine-ChooseCdkDeployOrDestroy": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.command",
          "StringEquals": "deploy",
          "Next": "awscdk-minecraftProvisionMcStateMachineCdkDeployMcServerBatchJob"
        },
        {
          "Variable": "$.command",
          "StringEquals": "destroy",
          "Next": "awscdk-minecraftProvisionMcStateMachineCdkDestroyMcServerBatchJob"
        }
      ]
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
          "Command": [
            "cdk",
            "deploy",
            "--app",
            "'python3 /app/app.py'",
            "--require-approval=never"
          ]
        }
      }
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
          "Command": [
            "cdk",
            "destroy",
            "--app",
            "'python3 /app/app.py'",
            "--force"
          ]
        }
      }
    }
  }
}


# write a fixture that creates a step functions state machine with boto
@pytest.fixture
@mock_stepfunctions
def state_machine_arn() -> str:
    """Create a step functions state machine with boto.

    Returns
    -------
    str
        The ARN of the state machine.
    """
    sfn_client: SFNClient = boto3.client("stepfunctions")
    create_state_machine: dict = sfn_client.create_state_machine(
        name="provision-minecraft-server-state-machine",
        definition=json.dumps(STATE_MACHINE_DEFINITION),
        roleArn="arn:aws:iam::123456789012:role/service-role/StepFunctions-ExecutionRole-us-east-1",
    )

    return create_state_machine["stateMachineArn"]


@pytest.fixture()
def test_client() -> TestClient:
    minecraft_pass_api = create_app()
    with TestClient(minecraft_pass_api) as client:
        yield client


def test_deploy(test_client: TestClient, state_machine_arn: str):
    response: Response = test_client.get("/deploy")
    assert response.status_code == HTTP_200_OK
    assert response.json() == "Success!"


def parse_execution_time(execution_time: str) -> datetime:
    return datetime.strptime(execution_time, "%Y-%m-%dT%H:%M:%S.%f%z")


def test_get_latest_execution(test_client: TestClient, state_machine_arn: str):
    response: Response = test_client.get("/latest-execution")
    assert response.status_code == HTTP_200_OK
    print("first /latest-execution")
    execution_start_time_1: datetime = parse_execution_time(response.json()["startDate"])

    # Does not impact mock, but allows resuse of this function for integration tests
    test_client.get("/deploy")

    response: Response = test_client.get("/latest-execution")
    assert response.status_code == HTTP_200_OK
    execution_start_time_2 = parse_execution_time(response.json()["startDate"])

    assert execution_start_time_1 < execution_start_time_2




