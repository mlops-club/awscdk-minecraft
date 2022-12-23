from typing import Optional

from minecraft_paas_api.aws.cloudformation import try_get_cloud_formation_stack_status
from minecraft_paas_api.aws.step_functions import get_latest_statemachine_execution
from minecraft_paas_api.schemas.server_status import DeploymentStatus

try:
    from mypy_boto3_cloudformation.literals import StackStatusType
    from mypy_boto3_stepfunctions.type_defs import ExecutionListItemTypeDef
except ImportError:
    print("Warning: failed to import boto3-stubs[cloudformation].")


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
    if minecraft_server_stack_status in ["CREATE_COMPLETE", "UPDATE_COMPLETE"]:
        return DeploymentStatus.SERVER_ONLINE

    if minecraft_server_stack_status in ["DELETE_COMPLETE", None]:
        return DeploymentStatus.SERVER_OFFLINE

    last_provisioner_execution: Optional[ExecutionListItemTypeDef] = get_latest_statemachine_execution(
        state_machine_arn=provision_server_state_machine_arn
    )
    if last_provisioner_execution and last_provisioner_execution["status"] == "RUNNING":
        return DeploymentStatus.SERVER_PROVISIONING
