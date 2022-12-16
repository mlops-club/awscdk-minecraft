from __future__ import annotations

from datetime import datetime

from minecraft_paas_api.services.service import IService
from minecraft_paas_api.settings import Settings


class MinecraftServerProvisioner(IService):
    def __init__(self, provisioner_state_machine_arn: str):
        self.provisioner_state_machine_arn = provisioner_state_machine_arn

    def init(self) -> None:
        pass

    @classmethod
    def from_settings(cls, settings: Settings) -> MinecraftServerProvisioner:
        return cls(provisioner_state_machine_arn=settings.provision_minecraft_server__state_machine__arn)

    def start_server_for_n_minutes(self, minutes_until_stop_server: int) -> None:
        pass

    def stop_server(self) -> None:
        pass

    def stop_server_in_n_minutes(self, minutes_until_stop_server: int) -> None:
        pass

    def cancel_stop_server(self) -> None:
        pass

    def is_server_starting(self) -> bool:
        pass

    def get_server_ip_address(self) -> str:
        """Return the IP address of the server."""

    def get_scheduled_server_stop_time(self) -> datetime:
        """Return the time the server is currently scheduled to be stopped."""


def save_destroy_server_execution_arn(self, execution_arn: str) -> None:
    ...


def get_destroy_server_execution_arn(self) -> str:
    ...
