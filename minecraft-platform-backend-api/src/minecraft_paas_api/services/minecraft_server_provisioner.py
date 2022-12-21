"""Module defines a classe that provisions minecraft server."""
from __future__ import annotations

from datetime import datetime

from minecraft_paas_api.services.service import IService
from minecraft_paas_api.settings import Settings


class MinecraftServerProvisioner(IService):
    """Class deines template for provisioning a Minecraft server."""

    def __init__(self, provisioner_state_machine_arn: str):
        self.provisioner_state_machine_arn = provisioner_state_machine_arn

    @classmethod
    def from_settings(cls, settings: Settings) -> MinecraftServerProvisioner:
        """Set the arn number for the state machine."""
        return cls(provisioner_state_machine_arn=settings.provision_minecraft_server__state_machine__arn)

    def start_server_for_n_minutes(self, minutes_until_stop_server: int) -> None:
        """Start and run the server for n number of minutes."""

    def stop_server(self) -> None:
        """Stop the server."""

    def stop_server_in_n_minutes(self, minutes_until_stop_server: int) -> None:
        """Stop the server in n minutes."""

    def cancel_stop_server(self) -> None:
        """Cancel stopping the server."""

    def is_server_starting(self) -> bool:
        """Is the server starting."""

    def get_server_ip_address(self) -> str:
        """Return the IP address of the server."""

    def get_scheduled_server_stop_time(self) -> datetime:
        """Return the time the server is currently scheduled to be stopped."""

    def save_destroy_server_execution_arn(self, execution_arn: str) -> None:
        """Save or destroy the server execution arn."""

    def get_destroy_server_execution_arn(self) -> str:
        """Save or destroy the server execution arn."""
