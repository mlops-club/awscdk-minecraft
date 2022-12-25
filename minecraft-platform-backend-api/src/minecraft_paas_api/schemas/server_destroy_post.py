"""Moduel defines pydantic module for the destroy server post requests."""

from pydantic import PositiveInt
from pydantic.main import BaseModel


class DestroyServer(BaseModel):
    """Response model for the `/destroy-server-after-seconds` endpoint."""

    time_to_wait_before_destroying_server: PositiveInt
