from datetime import datetime
from typing import Any, Dict, Optional, List

from fastapi import APIRouter

ROUTER = APIRouter()

state_machine_arn = "arn:aws:states:us-west-2:630013828440:stateMachine:awscdkminecraftProvisionMcStateMachineawscdkminecraftProvisionMcSta-aDmssJYgrn9o"
# https://us-west-2.console.aws.amazon.com/states/home?region=us-west-2#/statemachines/view/arn:aws:states:us-west-2:630013828440:stateMachine:awscdkminecraftProvisionMcStateMachineawscdkminecraftProvisionMcSta-aDmssJYgrn9o

# list the executions
# grab the most recent
# .... describe it

from time import sleep

try:
    from mypy_boto3_stepfunctions.client import SFNClient
    from mypy_boto3_stepfunctions.type_defs import DescribeStateMachineOutputTypeDef, ListExecutionsOutputTypeDef, ExecutionListItemTypeDef
except:
    print("Could not import boto3 stubs")


import boto3
import os

os.environ["AWS_PROFILE"] = "mlops-club"


# Questions that the functions in this module need to answer:
# TODO 1. Is the EC2 instance provisioned -> is it running?
# TODO 2. Is the minecraft docker container on the EC2 instance actually running and accepting traffic on 25565?
# TODO 3. CloudFormation:
#         Is the CloudFormation deployment running?
#         What is the most recent run of our batch job? What state is the AWS Batch Job in?
#         Is there a running execution of the state machine? If so, what state is it in? Timestamp?


# Can we hit the backend API from the frontend?



def describe_state_machine(state_machine_arn: str) -> DescribeStateMachineOutputTypeDef:
    sfn_client: SFNClient = boto3.client("stepfunctions")
    response: DescribeStateMachineOutputTypeDef = sfn_client.describe_state_machine(stateMachineArn=state_machine_arn)
    return response


def get_latest_statemachine_execution(state_machine_arn: str) -> Optional[ExecutionListItemTypeDef]:
    """Get the latest execution of a state machine."""
    sfn_client: SFNClient = boto3.client("stepfunctions")
    response: ListExecutionsOutputTypeDef = sfn_client.list_executions(
        stateMachineArn=state_machine_arn,
        maxResults=10,
    )

    executions: List[ExecutionListItemTypeDef] = sorted(response['executions'], key=lambda x: x["startDate"], reverse=True)
    latest_execution: ExecutionListItemTypeDef = executions[0] if len(executions) > 0 else None
    return latest_execution


@ROUTER.get("/state-machine-status")
def get_statemachine():
    return get_latest_statemachine_execution(state_machine_arn=state_machine_arn)
