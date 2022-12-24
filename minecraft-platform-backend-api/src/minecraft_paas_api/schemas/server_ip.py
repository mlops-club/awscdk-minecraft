"""Module defines pydantic schema for returning ip address from the server."""

import ipaddress

from pydantic import BaseModel, Field


class ServerIpSchema(BaseModel):
    """Response model for the `/minecraft_server_ip_address` endpoint."""

    server_ip_address: ipaddress.IPv4Address = Field(description="IPv4 address of the minecraft server.")
