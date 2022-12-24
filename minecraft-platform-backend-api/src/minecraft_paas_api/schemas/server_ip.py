"""Module defines pydantic schema for returning ip address from the server."""

import ipaddress

from pydantic import BaseModel


class ServerIpSchema(BaseModel):
    """Class defines the return schema for returnign the IP address of the server."""

    server_ip_address: ipaddress.IPv4Address
