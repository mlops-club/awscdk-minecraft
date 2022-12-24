from datetime import datetime, timedelta
from typing import Optional, TypedDict

from minecraft_paas_api.aws.cloudformation import try_get_cloud_formation_stack_status
from minecraft_paas_api.aws.step_functions import (
    get_latest_statemachine_execution,
    get_state_machine_execution_input,
    get_state_machine_execution_start_timestamp,
)
from minecraft_paas_api.schemas.server_status import DeploymentStatus
from typing_extensions import NotRequired

try:
    from mypy_boto3_cloudformation.literals import StackStatusType
    from mypy_boto3_stepfunctions.type_defs import ExecutionListItemTypeDef
except ImportError:
    print("Warning: failed to import boto3-stubs[cloudformation].")


class DestroyServerSfnInput(TypedDict):
    wait_n_minutes_before_deprovisioning: NotRequired[int]


def get_minecraft_server_status(
    minecraft_server_stack_name: str,
    provision_server_state_machine_arn: str,
    destroy_server_state_machine_arn: str = "",
) -> DeploymentStatus:
    """

    - `SERVER_OFFLINE`: The `awscdk-minecraft-server` CloudFormation stack does not exist or is in a `DELETE_COMPLETE` state.
    - `SERVER_PROVISIONING`: The latest execution of the `provision-minecraft-server` Step Function state machine
      is in a `RUNNING` state.
    - `SERVER_PROVISIONING_FAILED`: The latest execution of the `provision-minecraft-server` Step Function state machine
      is in a `FAILED` state.
    - `SERVER_ONLINE`: The `awscdk-minecraft-server` CloudFormation stack exists and is in a `CREATE_COMPLETE` state.
    - `SERVER_DEPROVISIONING`: The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine
      is in a `RUNNING` state AND the execution does not have a `wait_n_minutes_before_deprovisioning` input parameter.
    - `SERVER_DEPROVISIONING_FAILED`: The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine.

    Depending on which `FAILED` state is the most recent, the status will be
    `SERVER_PROVISIONING_FAILED` or `SERVER_DEPROVISIONING_FAILED`.
    """
    minecraft_server_stack_status: Optional["StackStatusType"] = try_get_cloud_formation_stack_status(
        stack_name=minecraft_server_stack_name
    )

    last_provisioner_execution: Optional[ExecutionListItemTypeDef] = get_latest_statemachine_execution(
        state_machine_arn=provision_server_state_machine_arn
    )

    # SERVER_PROVISIONING
    if last_provisioner_execution and last_provisioner_execution["status"] == "RUNNING":
        return DeploymentStatus.SERVER_PROVISIONING

    last_destroyer_execution: Optional[ExecutionListItemTypeDef] = get_latest_statemachine_execution(
        state_machine_arn=destroy_server_state_machine_arn
    )

    # SERVER_DEPROVISIONING
    if last_destroyer_execution and last_destroyer_execution["status"] == "RUNNING":
        execution_input: DestroyServerSfnInput = get_state_machine_execution_input(
            execution_arn=last_destroyer_execution["executionArn"]
        )
        if "wait_n_minutes_before_deprovisioning" not in execution_input:
            return DeploymentStatus.SERVER_DEPROVISIONING

        if "wait_n_minutes_before_deprovisioning" in execution_input:
            execution_start_time: datetime = get_state_machine_execution_start_timestamp(
                execution_arn=last_destroyer_execution["executionArn"]
            )
            wait_n_minutes_before_deprovisioning: int = execution_input["wait_n_minutes_before_deprovisioning"]
            scheduled_destroy_time: datetime = execution_start_time + timedelta(
                wait_n_minutes_before_deprovisioning
            )
            if datetime.utcnow() >= scheduled_destroy_time:
                return DeploymentStatus.SERVER_DEPROVISIONING

    # SERVER_PROVISIONING_FAILED or SERVER_DEPROVISIONING_FAILED
    if int(bool(last_provisioner_execution)) + int(bool(last_destroyer_execution)) == 1:
        if last_provisioner_execution and last_provisioner_execution["status"] == "FAILED":
            return DeploymentStatus.SERVER_PROVISIONING_FAILED
        if last_destroyer_execution and last_destroyer_execution["status"] == "FAILED":
            return DeploymentStatus.SERVER_DEPROVISIONING_FAILED

    # (continued) SERVER_PROVISIONING_FAILED or SERVER_DEPROVISIONING_FAILED
    if last_destroyer_execution and last_destroyer_execution:
        if last_destroyer_execution["status"] == last_provisioner_execution["status"] == "FAILED":
            provisioning_stop_time: datetime = get_state_machine_execution_start_timestamp(
                execution_arn=last_provisioner_execution["executionArn"]
            )
            deprovisioning_stop_time: datetime = get_state_machine_execution_start_timestamp(
                execution_arn=last_destroyer_execution["executionArn"]
            )
            last_failure_was_due_to_provisioning: bool = provisioning_stop_time >= deprovisioning_stop_time
            return (
                DeploymentStatus.SERVER_PROVISIONING_FAILED
                if last_failure_was_due_to_provisioning
                else DeploymentStatus.SERVER_DEPROVISIONING_FAILED
            )

    # SERVER_ONLINE
    if minecraft_server_stack_status in ["CREATE_COMPLETE", "UPDATE_COMPLETE"]:
        return DeploymentStatus.SERVER_ONLINE

    # SERVER_OFFLINE
    if minecraft_server_stack_status in ["DELETE_COMPLETE", None]:
        return DeploymentStatus.SERVER_OFFLINE

    # default? we should have returned something by now, but I can't prove that we have (yet)
