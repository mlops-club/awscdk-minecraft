"""Module defines a classe that provisions minecraft server."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Optional

from minecraft_paas_api.aws.cloudformation import (
    get_cloudform_output_value,
    try_get_cloud_formation_stack_status,
)
from minecraft_paas_api.aws.step_functions import (
    get_latest_statemachine_execution,
    get_state_machine_execution_input,
    get_state_machine_execution_start_timestamp,
    trigger_state_machine,
)
from minecraft_paas_api.schemas.server_status import DeploymentStatus
from minecraft_paas_api.services.service import IService
from minecraft_paas_api.settings import Settings
from mypy_boto3_cloudformation.literals import StackStatusType
from mypy_boto3_stepfunctions.type_defs import ExecutionListItemTypeDef, StartExecutionOutputTypeDef

from loguru import logger


class MinecraftServerProvisioner(IService):
    """Class deines template for provisioning a Minecraft server."""

    def __init__(
        self,
        provisioner_state_machine_arn: str,
        destroyer_state_machine_arn: str,
        cloudformation_stack_name: str,
        cloud_formation_server_ip_output_key_name: str,
    ):
        self.provisioner_state_machine_arn = provisioner_state_machine_arn
        self.destroyer_state_machine_arn = destroyer_state_machine_arn
        self.cloudformation_stack_name = cloudformation_stack_name
        self.cloud_formation_server_ip_output_key_name = cloud_formation_server_ip_output_key_name

    @classmethod
    def from_settings(cls, settings: Settings) -> MinecraftServerProvisioner:
        """Set the arn number for the state machine."""
        return cls(
            provisioner_state_machine_arn=settings.deploy_server_state_machine_arn,
            destroyer_state_machine_arn=settings.destroy_server_state_machine_arn,
            cloudformation_stack_name=settings.cloud_formation_stack_name,
            cloud_formation_server_ip_output_key_name=settings.cloud_formation_server_ip_output_key_name,
        )

    def start_server(self) -> StartExecutionOutputTypeDef:
        """Start the server."""
        return trigger_state_machine(state_machine_arn=self.provisioner_state_machine_arn, payload=None)

    def stop_server(self) -> StartExecutionOutputTypeDef:
        """Stop the server."""
        return trigger_state_machine(state_machine_arn=self.destroyer_state_machine_arn, payload=None)

    def stop_server_in_n_minutes(self, minutes_to_wait_until_stop_server: int) -> StartExecutionOutputTypeDef:
        """Stop the server in n seconds."""
        payload = {"wait_n_seconds_before_destroy": minutes_to_wait_until_stop_server * 60}
        return trigger_state_machine(state_machine_arn=self.destroyer_state_machine_arn, payload=payload)

    def cancel_stop_server(self) -> None:
        """Cancel stopping the server."""

    def is_server_starting(self) -> bool:
        """Is the server starting."""

    def get_server_ip_address(self) -> str:
        """Return the IP address of the server."""
        return get_cloudform_output_value(
            self.cloudformation_stack_name, self.cloud_formation_server_ip_output_key_name
        )

    def get_scheduled_server_stop_time(self) -> datetime:
        """Return the time the server is currently scheduled to be stopped."""

    def save_destroy_server_execution_arn(self, execution_arn: str) -> None:
        """Save or destroy the server execution arn."""

    def get_destroy_server_execution_arn(self) -> str:
        """Save or destroy the server execution arn."""

    def get_minecraft_server_status(self) -> DeploymentStatus:
        """
        Get the minecraft server status.

        - `SERVER_OFFLINE`: The `awscdk-minecraft-server` CloudFormation stack does not exist or is in a `DELETE_COMPLETE` state.
        - `SERVER_PROVISIONING`: The latest execution of the `provision-minecraft-server` Step Function state machine
          is in a `RUNNING` state.
        - `SERVER_PROVISIONING_FAILED`: The latest execution of the `provision-minecraft-server` Step Function state machine
          is in a `FAILED` state.
        - `SERVER_ONLINE`: The `awscdk-minecraft-server` CloudFormation stack exists and is in a `CREATE_COMPLETE` state.
        - `SERVER_DEPROVISIONING`: The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine
          is in a `RUNNING` state AND the execution does not have a `wait_n_seconds_before_destroy` input parameter.
        - `SERVER_DEPROVISIONING_FAILED`: The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine.

        Depending on which `FAILED` state is the most recent, the status will be
        `SERVER_PROVISIONING_FAILED` or `SERVER_DEPROVISIONING_FAILED`.
        """
        minecraft_server_stack_status: Optional["StackStatusType"] = try_get_cloud_formation_stack_status(
            stack_name=self.cloudformation_stack_name
        )
        logger.info(f"Cloudformation stack status: {minecraft_server_stack_status}")

        last_provisioner_execution: Optional[ExecutionListItemTypeDef] = get_latest_statemachine_execution(
            state_machine_arn=self.provisioner_state_machine_arn
        )
        logger.info(f"Last execution {last_provisioner_execution}")

        # SERVER_PROVISIONING
        if last_provisioner_execution and last_provisioner_execution["status"] == "RUNNING":
            logger.info("Server is provisioning")
            return DeploymentStatus.SERVER_PROVISIONING

        last_destroyer_execution: Optional[ExecutionListItemTypeDef] = get_latest_statemachine_execution(
            state_machine_arn=self.destroyer_state_machine_arn
        )
        logger.info(f"Last execution {last_destroyer_execution}")

        # SERVER_DEPROVISIONING
        if last_destroyer_execution and last_destroyer_execution["status"] == "RUNNING":
            execution_input: Dict = get_state_machine_execution_input(
                execution_arn=last_destroyer_execution["executionArn"]
            )
            if "wait_n_seconds_before_destroy" not in execution_input:
                return DeploymentStatus.SERVER_DEPROVISIONING

            if "wait_n_seconds_before_destroy" in execution_input:
                execution_start_time: datetime = get_state_machine_execution_start_timestamp(
                    execution_arn=last_destroyer_execution["executionArn"]
                )
                logger.info(f"Execution start time: {execution_start_time}")

                wait_n_seconds_before_destroy: int = execution_input["wait_n_seconds_before_destroy"]
                scheduled_destroy_time: datetime = execution_start_time + timedelta(
                    seconds=wait_n_seconds_before_destroy
                )

                scheduled_destroy_time: float = scheduled_destroy_time.timestamp()
                now: float = datetime.now().timestamp()

                if scheduled_destroy_time <= now:
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
                logger.info(f"Provisioning stop time: {provisioning_stop_time}")

                deprovisioning_stop_time: datetime = get_state_machine_execution_start_timestamp(
                    execution_arn=last_destroyer_execution["executionArn"]
                )
                logger.info(f"Deprovisioning stop time: {deprovisioning_stop_time}")

                last_failure_was_due_to_provisioning: bool = provisioning_stop_time >= deprovisioning_stop_time
                logger.info(f"Last failure was due to provisioning: {last_failure_was_due_to_provisioning}")

                return (
                    DeploymentStatus.SERVER_PROVISIONING_FAILED
                    if last_failure_was_due_to_provisioning
                    else DeploymentStatus.SERVER_DEPROVISIONING_FAILED
                )

        # SERVER_ONLINE
        if minecraft_server_stack_status in ["CREATE_COMPLETE", "UPDATE_COMPLETE"]:
            logger.info("Server is online")
            return DeploymentStatus.SERVER_ONLINE

        # SERVER_OFFLINE
        if minecraft_server_stack_status in ["DELETE_COMPLETE", None]:
            logger.info("Server is offline")
            return DeploymentStatus.SERVER_OFFLINE

        # default? we should have returned something by now, but I can't prove that we have (yet)
