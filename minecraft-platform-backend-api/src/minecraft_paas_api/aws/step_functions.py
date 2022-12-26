from __future__ import annotations

import json
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Optional

import boto3

try:
    from mypy_boto3_stepfunctions.client import SFNClient
    from mypy_boto3_stepfunctions.type_defs import (
        DescribeExecutionOutputTypeDef,
        DescribeStateMachineOutputTypeDef,
        ExecutionListItemTypeDef,
        ListExecutionsOutputTypeDef,
        StartExecutionOutputTypeDef,
    )
except ImportError:
    print("Warning: boto3-stubs[stepfunctions] not installed")


def trigger_state_machine(state_machine_arn: str, payload: Optional[Dict]) -> "StartExecutionOutputTypeDef":
    """Send command to state machine.

    :param payload: A JSON-serializable dictionary to provide as the execution input.
    :param state_machine_arn: The ARN of the state machine to execute.

    :raises boto3.exceptions.ClientError: If the state machine could not be triggered.
    """
    if payload is None:
        payload = {}
    sfn_client: SFNClient = boto3.client("stepfunctions")
    start_execuction_response: "StartExecutionOutputTypeDef" = sfn_client.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps(payload),
    )
    return start_execuction_response


def describe_state_machine(state_machine_arn: str) -> "DescribeStateMachineOutputTypeDef":
    """
    Describe a state machine including its definition.

    :param state_machine_arn: The ARN of the state machine to describe.
    """
    sfn_client: "SFNClient" = boto3.client("stepfunctions")
    # TO DO: Add try except
    response: "DescribeStateMachineOutputTypeDef" = sfn_client.describe_state_machine(
        stateMachineArn=state_machine_arn
    )
    return response


def get_latest_statemachine_execution(state_machine_arn: str) -> Optional["ExecutionListItemTypeDef"]:
    """
    Get the latest execution of a state machine.

    :param state_machine_arn: The ARN of the state machine to query.
    :return: The latest execution of the state machine, or None if there are no executions.
    """
    sfn_client: "SFNClient" = boto3.client("stepfunctions")
    # TO DO: Add try except
    response: ListExecutionsOutputTypeDef = sfn_client.list_executions(
        stateMachineArn=state_machine_arn,
        maxResults=10,
    )
    executions: List["ExecutionListItemTypeDef"] = sorted(
        response["executions"], key=lambda x: x["startDate"], reverse=True
    )
    latest_execution: "ExecutionListItemTypeDef" = executions[0] if len(executions) > 0 else None
    return latest_execution


@lru_cache
def describe_state_machine_execution(execution_arn: str) -> "DescribeExecutionOutputTypeDef":
    """
    Get the input of a state machine execution.

    :param execution_arn: The ARN of the execution to query.
    :return: The input of the execution, or None if the execution does not exist.
    """
    sfn_client: "SFNClient" = boto3.client("stepfunctions")
    # TO DO: Add try except
    response: "DescribeExecutionOutputTypeDef" = sfn_client.describe_execution(
        executionArn=execution_arn,
    )
    return response


def get_state_machine_execution_input(execution_arn: str) -> Dict:
    """
    Get the input of a state machine execution.

    :param execution_arn: The ARN of the execution to query.
    :return: The input of the execution, or None if the execution does not exist.
    """
    execution: "DescribeExecutionOutputTypeDef" = describe_state_machine_execution(execution_arn)
    return json.loads(execution["input"])


def get_state_machine_execution_start_timestamp(execution_arn: str) -> datetime:
    """
    Get the start timestamp of a state machine execution.

    :param execution_arn: The ARN of the execution to query.
    :return: The start timestamp of the execution, or None if the execution does not exist.
    """
    execution: "DescribeExecutionOutputTypeDef" = describe_state_machine_execution(execution_arn)
    return execution["startDate"]


def get_state_machine_execution_end_timestamp(execution_arn: str) -> datetime:
    """
    Get the end timestamp of a state machine execution.

    :param execution_arn: The ARN of the execution to query.
    :return: The end timestamp of the execution, or None if the execution does not exist.
    """
    execution: "DescribeExecutionOutputTypeDef" = describe_state_machine_execution(execution_arn)
    return execution["stopDate"]
