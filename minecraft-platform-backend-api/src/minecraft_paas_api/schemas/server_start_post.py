"""Pydantic model for start server POST request."""


from pydantic import conint
from pydantic.main import BaseModel


class StartServerRequestPayload(BaseModel):
    """Response model for the `/destroy-server-after-seconds` endpoint."""

    play_time_minutes: conint(ge=30)
